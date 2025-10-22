from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.types import Forbidden
from chalicelib.types import NewSong
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import Song
from chalicelib.types import SongList
from chalicelib.types import UpdateSong

bp = Blueprint(__name__)


@bp.route("/songs", methods=["GET"])
def list_songs() -> Forbidden | SongList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, title, credits, ccli_num, tags, created_on, creator_id "
            "FROM songs "
            "ORDER BY title",
            output=Song,
        )
        return SongList(songs=curs.fetchall())


@bp.route("/songs", methods=["POST"])
def new_song(request_body: NewSong) -> Forbidden | Song:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO songs (title, credits, ccli_num, tags) "
            "VALUES (:title, :credits, :ccli_num, :tags) "
            "RETURNING id, title, credits, ccli_num, tags, created_on, creator_id",
            request_body,
            output=Song,
        )
        song = curs.fetchone()
        assert song is not None

    return song


@bp.route("/songs/{song_id}", methods=["GET"])
def get_song(song_id: str) -> Forbidden | NotFound | Song:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, title, credits, ccli_num, tags, created_on, creator_id "
            "FROM songs WHERE id = :id",
            {"id": song_id},
            output=Song,
        )
        song = curs.fetchone()
        return song if song is not None else NotFound()


@bp.route("/songs/{song_id}", methods=["PUT"])
def update_song(
    song_id: str, request_body: UpdateSong
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE songs SET {request_body.replacement_sql} WHERE id = :id",
            {"id": song_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()
