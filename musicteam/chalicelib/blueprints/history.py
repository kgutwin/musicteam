from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.types import _SparkLineHistoryRow
from chalicelib.types import Forbidden
from chalicelib.types import NotFound
from chalicelib.types import SongHistory
from chalicelib.types import SparkLineHistory
from chalicelib.types import SparkLineHistoryPoint
from chalicelib.types import TopSong
from chalicelib.types import TopSongParams
from chalicelib.types import TopSongs

bp = Blueprint(__name__)


@bp.route("/history/song/{song_id}", methods=["GET"])
def get_song_history(song_id: str) -> Forbidden | NotFound | SongHistory:
    """Get song history data"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        row = conn.execute(
            "WITH song_setlists AS ("
            "  SELECT setlist_id, setlist_service_date"
            "  FROM song_history"
            "  WHERE song_id = :song_id"
            "  ORDER BY setlist_service_date ASC"
            ") SELECT"
            "  last(setlist_service_date) AS recent_played,"
            "  last(setlist_id) AS recent_played_setlist_id,"
            "  first(setlist_service_date) AS first_played,"
            "  first(setlist_id) AS first_played_setlist_id,"
            "  count(*) AS num_played,"
            "  count(*) FILTER ("
            "    WHERE setlist_service_date > (current_date - 365)"
            "  ) AS num_played_past_year "
            "FROM song_setlists",
            {"song_id": song_id},
            output=SongHistory,
        ).fetchone()
        return row if row is not None else NotFound()


@bp.route("/history/sparkline", methods=["GET"])
def get_history_sparkline() -> Forbidden | SparkLineHistory:
    """Get history data suitable for spark line render"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  date_trunc('month', setlist_service_date) AS month_year,"
            "  song_id,"
            "  count(setlist_id) AS appearances "
            "FROM song_history "
            "WHERE date_trunc('month', setlist_service_date) > date_trunc('month', current_date - (365 * 2)) "
            "GROUP BY song_id, month_year",
            output=_SparkLineHistoryRow,
        )

        rv = SparkLineHistory(songs={})
        for row in curs.fetchall():
            rv.songs.setdefault(row.song_id, []).append(
                SparkLineHistoryPoint(mo_yr=row.month_year, count=row.appearances)
            )
        for song in rv.songs:
            rv.songs[song].sort()

        return rv


@bp.route("/history/topSongs", methods=["GET"])
def get_history_top_songs(query_params: TopSongParams) -> Forbidden | TopSongs:
    """Get the top songs based on various methods"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    if query_params.ranking == "alltime":
        query = """
WITH top_songs AS (
  SELECT song_id, count(setlist_id) AS appearances
  FROM song_history
  GROUP BY song_id
  ORDER BY appearances DESC
  LIMIT :num
)
SELECT
  songs.id, songs.title, songs.authors, songs.ccli_num, songs.tags, songs.created_on,
  songs.creator_id, songs.last_modified, top_songs.appearances
FROM top_songs
INNER JOIN songs ON songs.id = top_songs.song_id
        """
    elif query_params.ranking == "recent":
        query = """
WITH top_songs AS (
  SELECT song_id, count(setlist_id) AS appearances
  FROM song_history
  GROUP BY song_id
  ORDER BY max(setlist_service_date) DESC, appearances DESC
  LIMIT :num
)
SELECT
  songs.id, songs.title, songs.authors, songs.ccli_num, songs.tags, songs.created_on,
  songs.creator_id, songs.last_modified, top_songs.appearances
FROM top_songs
INNER JOIN songs ON songs.id = top_songs.song_id
        """
    elif query_params.ranking == "weighted":
        query = """
WITH top_songs AS (
  SELECT
    song_id,
    sum(power(2.0, (setlist_service_date - current_date) / 365.0)) AS appearances
  FROM song_history
  GROUP BY song_id
  ORDER BY appearances DESC
  LIMIT :num
)
SELECT
  songs.id, songs.title, songs.authors, songs.ccli_num, songs.tags, songs.created_on,
  songs.creator_id, songs.last_modified, top_songs.appearances
FROM top_songs
INNER JOIN songs ON songs.id = top_songs.song_id
        """

    with db.connect() as conn:
        curs = conn.execute(query, {"num": query_params.num}, output=TopSong)
        return TopSongs(songs=curs.fetchall())
