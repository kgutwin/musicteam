from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.types import Forbidden
from chalicelib.types import NotFound
from chalicelib.types import SongHistory

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
