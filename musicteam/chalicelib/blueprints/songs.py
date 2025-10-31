from chalice.app import Blueprint
from chalicelib import db
from chalicelib.config import OBJECT_BUCKET_NAME
from chalicelib.middleware import session_role
from chalicelib.middleware import session_user
from chalicelib.storage import s3
from chalicelib.types import _SongSheetObject
from chalicelib.types import Download
from chalicelib.types import Forbidden
from chalicelib.types import NewSong
from chalicelib.types import NewSongSheet
from chalicelib.types import NewSongVersion
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import PartialDownload
from chalicelib.types import Song
from chalicelib.types import SongList
from chalicelib.types import SongSheet
from chalicelib.types import SongSheetList
from chalicelib.types import SongVersion
from chalicelib.types import SongVersionList
from chalicelib.types import UpdateSong
from chalicelib.types import UpdateSongSheet
from chalicelib.types import UpdateSongVersion

bp = Blueprint(__name__)


@bp.route("/songs", methods=["GET"])
def list_songs() -> Forbidden | SongList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, title, authors, ccli_num, tags, created_on, creator_id "
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
            "INSERT INTO songs (title, authors, ccli_num, tags, creator_id) "
            "VALUES (:title, :authors, :ccli_num, :tags, :creator_id) "
            "RETURNING id, title, authors, ccli_num, tags, created_on, creator_id",
            request_body.model_dump()
            | {"creator_id": session_user(bp.current_request).id},
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
            "SELECT id, title, authors, ccli_num, tags, created_on, creator_id "
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

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE songs SET {request_body.replacement_sql} WHERE id = :id",
            {"id": song_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}", methods=["DELETE"])
def delete_song(song_id: str) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute("DELETE FROM songs WHERE id = :id", {"id": song_id})
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}/versions", methods=["GET"])
def list_song_versions(song_id: str) -> Forbidden | SongVersionList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, song_id, label, verse_order, lyrics, tags, created_on,"
            "    creator_id "
            "FROM song_versions WHERE song_id = :song_id "
            "ORDER BY label",
            {"song_id": song_id},
            output=SongVersion,
        )
        return SongVersionList(song_versions=curs.fetchall())


@bp.route("/songs/{song_id}/versions", methods=["POST"])
def new_song_version(
    song_id: str, request_body: NewSongVersion
) -> Forbidden | SongVersion:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO song_versions ("
            "    song_id, label, verse_order, lyrics, tags, creator_id"
            ") VALUES ("
            "    :song_id, :label, :verse_order, :lyrics, :tags, :creator_id"
            ") "
            "RETURNING id, song_id, label, verse_order, lyrics, tags, created_on,"
            "    creator_id",
            request_body.model_dump()
            | {"song_id": song_id, "creator_id": session_user(bp.current_request).id},
            output=SongVersion,
        )
        song_version = curs.fetchone()
        assert song_version is not None

    return song_version


@bp.route("/songs/{song_id}/versions/{version_id}", methods=["GET"])
def get_song_version(
    song_id: str, version_id: str
) -> Forbidden | NotFound | SongVersion:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, song_id, label, verse_order, lyrics, tags, created_on, creator_id "
            "FROM song_versions WHERE id = :version_id AND song_id = :song_id",
            {"song_id": song_id, "version_id": version_id},
            output=SongVersion,
        )
        song_version = curs.fetchone()
        return song_version if song_version is not None else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}", methods=["PUT"])
def update_song_version(
    song_id: str, version_id: str, request_body: UpdateSongVersion
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE song_versions SET {request_body.replacement_sql} "
            f"WHERE id = :version_id AND song_id = :song_id",
            {"version_id": version_id, "song_id": song_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}", methods=["DELETE"])
def delete_song_version(
    song_id: str, version_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM song_versions WHERE id = :version_id AND song_id = :song_id",
            {"version_id": version_id, "song_id": song_id},
        )
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}/sheets", methods=["GET"])
def list_song_sheets(song_id: str, version_id: str) -> Forbidden | SongSheetList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "    id, song_version_id, type, key, tags, object_id, object_type,"
            "    created_on, creator_id "
            "FROM song_sheets WHERE song_version_id = :version_id "
            "ORDER BY key",
            {"version_id": version_id},
            output=SongSheet,
        )
        return SongSheetList(song_sheets=curs.fetchall())


@bp.route("/songs/{song_id}/versions/{version_id}/sheets", methods=["POST"])
def new_song_sheet(
    song_id: str, version_id: str, request_body: NewSongSheet
) -> Forbidden | SongSheet:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO song_sheets ("
            "    song_version_id, type, key, tags, object_id, object_type, creator_id"
            ") VALUES ("
            "    :song_version_id, :type, :key, :tags, :object_id, :object_type,"
            "    :creator_id"
            ") "
            "RETURNING id, song_version_id, type, key, tags, object_id, object_type,"
            "    created_on, creator_id",
            request_body.model_dump()
            | {
                "song_version_id": version_id,
                "creator_id": session_user(bp.current_request).id,
            },
            output=SongSheet,
        )
        song_sheet = curs.fetchone()
        assert song_sheet is not None

    return song_sheet


@bp.route("/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}", methods=["GET"])
def get_song_sheet(
    song_id: str, version_id: str, sheet_id: str
) -> Forbidden | NotFound | SongSheet:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, song_version_id, type, key, tags, object_id, object_type,"
            "  created_on, creator_id "
            "FROM song_sheets WHERE id = :sheet_id AND song_version_id = :version_id",
            {"sheet_id": sheet_id, "version_id": version_id},
            output=SongSheet,
        )
        song_sheet = curs.fetchone()
        return song_sheet if song_sheet is not None else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}", methods=["PUT"])
def update_song_sheet(
    song_id: str, version_id: str, sheet_id: str, request_body: UpdateSongSheet
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE song_sheets SET {request_body.replacement_sql} "
            f"WHERE id = :sheet_id AND song_version_id = :version_id",
            {"sheet_id": sheet_id, "version_id": version_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route(
    "/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}", methods=["DELETE"]
)
def delete_song_sheet(
    song_id: str, version_id: str, sheet_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM song_sheets "
            "WHERE id = :sheet_id AND song_version_id = :version_id",
            {"sheet_id": sheet_id, "version_id": version_id},
        )
        return NoContent() if result else NotFound()


@bp.route(
    "/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}/doc",
    methods=["HEAD", "GET"],
)
def get_song_sheet_doc(
    song_id: str, version_id: str, sheet_id: str
) -> Forbidden | NotFound | Download | PartialDownload:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT object_type, object_id "
            "FROM song_sheets WHERE id = :sheet_id AND song_version_id = :version_id",
            {"sheet_id": sheet_id, "version_id": version_id},
            output=_SongSheetObject,
        )
        sheet_obj = curs.fetchone()
        if sheet_obj is None:
            return NotFound()

    content_type = sheet_obj.object_type

    if bp.current_request.method == "HEAD":
        s3_resp = s3.head_object(Bucket=OBJECT_BUCKET_NAME, Key=sheet_obj.object_id)
        return Download(
            b"",
            headers={
                "Content-Type": content_type,
                "Accept-Ranges": "bytes",
                "Content-Length": str(s3_resp["ContentLength"]),
            },
        )

    extra: dict[str, str] = {}
    if bp.current_request.headers.get("Range"):
        extra["Range"] = bp.current_request.headers["Range"]

    s3_resp = s3.get_object(Bucket=OBJECT_BUCKET_NAME, Key=sheet_obj.object_id, **extra)

    headers: dict[str, str | list[str]] = {
        "Content-Type": content_type,
    }
    body = s3_resp["Body"].read()
    if content_type == "text/plain":
        # if we uploaded a file which can't be read as utf-8, then
        # chalice is going to have problems with it, so replace bad
        # bytes with the unknown character.
        body = body.decode(errors="replace").encode()

    if bp.current_request.headers.get("Range"):
        headers["Content-Range"] = s3_resp["ContentRange"]
        return PartialDownload(body, headers=headers)
    else:
        return Download(body, headers=headers)
