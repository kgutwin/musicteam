from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.middleware import session_user
from chalicelib.storage import get_download
from chalicelib.types import _Object
from chalicelib.types import _SearchSongRow
from chalicelib.types import BadRequest
from chalicelib.types import Download
from chalicelib.types import Forbidden
from chalicelib.types import Found
from chalicelib.types import ListSongParams
from chalicelib.types import NewSong
from chalicelib.types import NewSongMedia
from chalicelib.types import NewSongSheet
from chalicelib.types import NewSongVersion
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import PartialDownload
from chalicelib.types import SearchSongList
from chalicelib.types import SearchSongParams
from chalicelib.types import Song
from chalicelib.types import SongList
from chalicelib.types import SongMedia
from chalicelib.types import SongMediaList
from chalicelib.types import SongRevision
from chalicelib.types import SongRevisionList
from chalicelib.types import SongRevisionSong
from chalicelib.types import SongRevisionSongSheet
from chalicelib.types import SongRevisionSongVersion
from chalicelib.types import SongSheet
from chalicelib.types import SongSheetList
from chalicelib.types import SongVersion
from chalicelib.types import SongVersionList
from chalicelib.types import UpdateSong
from chalicelib.types import UpdateSongMedia
from chalicelib.types import UpdateSongSheet
from chalicelib.types import UpdateSongVersion

bp = Blueprint(__name__)


@bp.route("/songs", methods=["GET"])
def list_songs(query_params: ListSongParams) -> Forbidden | SongList:
    """List songs

    All filter parameters are optional. When no filters are provided,
    all songs on the site will be returned.

    """
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        where_clauses = []
        params: dict[str, str | int] = {}
        if query_params.ccli_num:
            where_clauses.append("ccli_num = :ccli_num")
            params["ccli_num"] = query_params.ccli_num
        if query_params.title:
            where_clauses.append("title ~* :title")
            params["title"] = query_params.title

        where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        curs = conn.execute(
            f"SELECT"
            f"  id, title, authors, ccli_num, tags, created_on, creator_id,"
            f"  last_modified "
            f"FROM songs {where} "
            f"ORDER BY title",
            params,
            output=Song,
        )
        return SongList(songs=curs.fetchall())


@bp.route("/songs", methods=["POST"])
def new_song(request_body: NewSong) -> Forbidden | Song:
    """Create a new song

    NOTE: To attach a sheet to a song, you will need to create a song
    version, then upload the sheet as an object, then create a song
    sheet that references that object.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO songs (title, authors, ccli_num, tags, creator_id) "
            "VALUES (:title, :authors, :ccli_num, :tags, :creator_id) "
            "RETURNING id, title, authors, ccli_num, tags, created_on, creator_id,"
            "          last_modified",
            request_body.model_dump()
            | {"creator_id": session_user(bp.current_request).id},
            output=Song,
        )
        song = curs.fetchone()
        assert song is not None

    return song


@bp.route("/songs/{song_id}", methods=["GET"])
def get_song(song_id: str) -> Forbidden | NotFound | Song:
    """Retrieve a single song by ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, title, authors, ccli_num, tags, created_on, creator_id,"
            "  last_modified "
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
    """Update a song's fields"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
        result = conn.execute(
            f"UPDATE songs SET {request_body.replacement_sql} WHERE id = :id",
            {"id": song_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}", methods=["DELETE"])
def delete_song(song_id: str) -> BadRequest | Forbidden | NotFound | NoContent:
    """Delete a song

    NOTE: A song cannot be deleted if it is referenced in a setlist.
    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
        try:
            result = conn.execute("DELETE FROM songs WHERE id = :id", {"id": song_id})
            return NoContent() if result else NotFound()
        except db.ForeignKeyViolation:
            return BadRequest(
                "Unable to delete songs that have been added to a set list"
            )


@bp.route("/songs/{song_id}/revisions", methods=["GET"])
def list_song_revisions(song_id: str) -> Forbidden | SongRevisionList:
    """List song revisions for a given song ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        rev_songs = conn.execute(
            "SELECT rev_id, 'song' AS rev_type, rev_created_on, rev_changed_by,"
            "    id, title, authors, ccli_num, tags "
            "FROM rev_songs WHERE id = :song_id "
            "ORDER BY rev_created_on DESC",
            {"song_id": song_id},
            output=SongRevisionSong,
        ).fetchall()

        rev_song_versions = conn.execute(
            "SELECT rev_id, 'song_version' AS rev_type, rev_created_on, rev_changed_by,"
            "    id, song_id, label, verse_order, lyrics, tags "
            "FROM rev_song_versions WHERE song_id = :song_id "
            "ORDER BY rev_created_on DESC",
            {"song_id": song_id},
            output=SongRevisionSongVersion,
        ).fetchall()

        rev_song_sheets = conn.execute(
            "SELECT rev_id, 'song_sheet' AS rev_type, rev_created_on, rev_changed_by,"
            "    id, song_id, song_version_id, type, key, tags, object_id, object_type "
            "FROM rev_song_sheets WHERE song_id = :song_id "
            "ORDER BY rev_created_on DESC",
            {"song_id": song_id},
            output=SongRevisionSongSheet,
        ).fetchall()

        all_revs: list[SongRevision] = rev_songs + rev_song_versions + rev_song_sheets

        return SongRevisionList(
            song_revisions=sorted(
                all_revs, reverse=True, key=lambda r: r.rev_created_on
            )
        )


@bp.route("/songs/{song_id}/versions", methods=["GET"])
def list_song_versions(song_id: str) -> Forbidden | SongVersionList:
    """List song versions for a given song ID"""
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
    """Create a new song version"""
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
    """Retrieve a single song version by ID"""
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
    """Update the fields of a song version"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
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
) -> BadRequest | Forbidden | NotFound | NoContent:
    """Delete a song version

    NOTE: A song version cannot be deleted if it is included in a setlist.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
        try:
            result = conn.execute(
                "DELETE FROM song_versions "
                "WHERE id = :version_id AND song_id = :song_id",
                {"version_id": version_id, "song_id": song_id},
            )
            return NoContent() if result else NotFound()
        except db.ForeignKeyViolation:
            return BadRequest(
                "Unable to delete song versions that have been added to a set list"
            )


@bp.route("/songs/{song_id}/versions/{version_id}/sheets", methods=["GET"])
def list_song_sheets(song_id: str, version_id: str) -> Forbidden | SongSheetList:
    """List song sheets for a given song and version ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "    id, song_version_id, type, key, tags, object_id, object_type,"
            "    auto_verse_order, created_on, creator_id "
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
    """Create a new song sheet for a song version

    To attach an object to a song sheet, first use the `/objects`
    method to upload your object, then provide the resulting ID as the
    `object_id` field.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO song_sheets ("
            "    song_version_id, type, key, tags, object_id, object_type,"
            "    auto_verse_order, creator_id"
            ") VALUES ("
            "    :song_version_id, :type, :key, :tags, :object_id, :object_type,"
            "    :auto_verse_order, :creator_id"
            ") "
            "RETURNING id, song_version_id, type, key, tags, object_id, object_type,"
            "    auto_verse_order, created_on, creator_id",
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
    """Retrieve a single song sheet by ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, song_version_id, type, key, tags, object_id, object_type,"
            "  auto_verse_order, created_on, creator_id "
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
    """Update the fields of a song sheet"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
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
) -> BadRequest | Forbidden | NotFound | NoContent:
    """Delete a song sheet

    NOTE: a song sheet cannot be deleted if it is included in a setlist.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        conn.set_session_id(session_user(bp.current_request).id)
        try:
            result = conn.execute(
                "DELETE FROM song_sheets "
                "WHERE id = :sheet_id AND song_version_id = :version_id",
                {"sheet_id": sheet_id, "version_id": version_id},
            )
            return NoContent() if result else NotFound()
        except db.ForeignKeyViolation:
            return BadRequest(
                "Unable to delete song sheets that have been added to a set list"
            )


@bp.route(
    "/songs/{song_id}/versions/{version_id}/sheets/{sheet_id}/doc",
    methods=["HEAD", "GET"],
)
def get_song_sheet_doc(
    song_id: str, version_id: str, sheet_id: str
) -> Forbidden | NotFound | Download | PartialDownload | Found:
    """Retrieve the document associated with a song sheet

    This method supports range requests.

    For large responses, this method returns a 302 Found temporary redirect.
    """
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT object_type, object_id "
            "FROM song_sheets WHERE id = :sheet_id AND song_version_id = :version_id",
            {"sheet_id": sheet_id, "version_id": version_id},
            output=_Object,
        )
        sheet_obj = curs.fetchone()
        if sheet_obj is None:
            return NotFound()

    return get_download(
        sheet_obj.object_id,
        sheet_obj.object_type,
        bp.current_request.method == "HEAD",
        bp.current_request.headers.get("Range"),
    )


@bp.route("/songs/{song_id}/versions/{version_id}/media", methods=["GET"])
def list_song_media(song_id: str, version_id: str) -> Forbidden | SongMediaList:
    """List media for a given song and version ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "    id, song_version_id, title, url, object_id, media_type, tags,"
            "    created_on, creator_id "
            "FROM song_media WHERE song_version_id = :version_id "
            "ORDER BY created_on",
            {"version_id": version_id},
            output=SongMedia,
        )
        return SongMediaList(song_media=curs.fetchall())


@bp.route("/songs/{song_id}/versions/{version_id}/media", methods=["POST"])
def new_song_media(
    song_id: str, version_id: str, request_body: NewSongMedia
) -> Forbidden | SongMedia:
    """Create a new media entry for a song version

    To attach an object to a media entry, first use the `/objects`
    method to upload your object, then provide the resulting ID as the
    `object_id` field.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO song_media ("
            "    song_version_id, title, url, object_id, media_type, tags,"
            "    creator_id"
            ") VALUES ("
            "    :song_version_id, :title, :url, :object_id, :media_type, :tags,"
            "    :creator_id"
            ") "
            "RETURNING id, song_version_id, title, url, object_id, media_type, tags,"
            "    created_on, creator_id",
            request_body.model_dump()
            | {
                "song_version_id": version_id,
                "creator_id": session_user(bp.current_request).id,
            },
            output=SongMedia,
        )
        song_media = curs.fetchone()
        assert song_media is not None

    return song_media


@bp.route("/songs/{song_id}/versions/{version_id}/media/{media_id}", methods=["GET"])
def get_song_media(
    song_id: str, version_id: str, media_id: str
) -> Forbidden | NotFound | SongMedia:
    """Retrieve a single song media by ID"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, song_version_id, title, url, object_id, media_type, tags,"
            "  created_on, creator_id "
            "FROM song_media WHERE id = :media_id AND song_version_id = :version_id",
            {"media_id": media_id, "version_id": version_id},
            output=SongMedia,
        )
        song_media = curs.fetchone()
        return song_media if song_media is not None else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}/media/{media_id}", methods=["PUT"])
def update_song_media(
    song_id: str, version_id: str, media_id: str, request_body: UpdateSongMedia
) -> Forbidden | NotFound | NoContent:
    """Update the fields of a media entry"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE song_media SET {request_body.replacement_sql} "
            f"WHERE id = :media_id AND song_version_id = :version_id",
            {"media_id": media_id, "version_id": version_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/songs/{song_id}/versions/{version_id}/media/{media_id}", methods=["DELETE"])
def delete_song_media(
    song_id: str, version_id: str, media_id: str
) -> Forbidden | NotFound | NoContent:
    """Delete a media entry for a song version"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM song_media "
            "WHERE id = :media_id AND song_version_id = :version_id",
            {"media_id": media_id, "version_id": version_id},
        )
        return NoContent() if result else NotFound()


@bp.route(
    "/songs/{song_id}/versions/{version_id}/media/{media_id}/obj",
    methods=["HEAD", "GET"],
)
def get_song_media_attachment(
    song_id: str, version_id: str, media_id: str
) -> Forbidden | NotFound | Download | PartialDownload | Found:
    """Retrieve the attachment associated with a song media

    This method supports range requests.

    For large responses, this method returns a 302 Found temporary redirect.
    """
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT media_type AS object_type, object_id "
            "FROM song_media "
            "WHERE id = :media_id AND song_version_id = :version_id "
            "AND object_id IS NOT NULL",
            {"media_id": media_id, "version_id": version_id},
            output=_Object,
        )
        media_obj = curs.fetchone()
        if media_obj is None:
            return NotFound()

    return get_download(
        media_obj.object_id,
        media_obj.object_type,
        bp.current_request.method == "HEAD",
        bp.current_request.headers.get("Range"),
    )


@bp.route("/songs/search", methods=["GET"])
def search_songs(query_params: SearchSongParams) -> Forbidden | SearchSongList:
    """Search for songs"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "WITH song_hits AS ("
            "  SELECT"
            "    song_id,"
            "    max("
            "      ts_rank_cd(lyrics_tsv, websearch_to_tsquery('english', :query))"
            "    ) AS rank,"
            "    any_value("
            "      ts_headline("
            "        'english', lyrics, websearch_to_tsquery('english', :query),"
            "        'MaxFragments=4'"
            "      )"
            "    ) AS highlighted"
            "  FROM song_versions"
            "  WHERE lyrics_tsv @@ websearch_to_tsquery('english', :query)"
            "  GROUP BY song_id"
            ") "
            "SELECT"
            "  songs.id,"
            "  songs.title,"
            "  songs.authors,"
            "  songs.ccli_num,"
            "  songs.tags,"
            "  songs.created_on,"
            "  songs.creator_id,"
            "  songs.last_modified,"
            "  song_hits.rank, "
            "  song_hits.highlighted "
            "FROM songs "
            "INNER JOIN song_hits ON songs.id = song_hits.song_id "
            "ORDER BY song_hits.rank DESC",
            {"query": query_params.q},
            output=_SearchSongRow,
        )
        return SearchSongList(hits=[row.hit for row in curs.fetchall()])
