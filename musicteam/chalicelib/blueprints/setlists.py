from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.middleware import session_user
from chalicelib.types import Forbidden
from chalicelib.types import NewSetlist
from chalicelib.types import NewSetlistPosition
from chalicelib.types import NewSetlistSheet
from chalicelib.types import NewSetlistTemplate
from chalicelib.types import NewSetlistTemplatePosition
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import Setlist
from chalicelib.types import SetlistList
from chalicelib.types import SetlistPosition
from chalicelib.types import SetlistPositionList
from chalicelib.types import SetlistSheet
from chalicelib.types import SetlistSheetList
from chalicelib.types import SetlistTemplate
from chalicelib.types import SetlistTemplateList
from chalicelib.types import SetlistTemplatePosition
from chalicelib.types import SetlistTemplatePositionList
from chalicelib.types import UpdateSetlist
from chalicelib.types import UpdateSetlistPosition
from chalicelib.types import UpdateSetlistSheet
from chalicelib.types import UpdateSetlistTemplate
from chalicelib.types import UpdateSetlistTemplatePosition

bp = Blueprint(__name__)


@bp.route("/setlists", methods=["GET"])
def list_setlists() -> Forbidden | SetlistList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, leader_name, service_date, tags, created_on, creator_id "
            "FROM setlists "
            "ORDER BY service_date DESC",
            output=Setlist,
        )
        return SetlistList(setlists=curs.fetchall())


@bp.route("/setlists", methods=["POST"])
def new_setlist(request_body: NewSetlist) -> Forbidden | Setlist:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO setlists (leader_name, service_date, tags, creator_id) "
            "VALUES (:leader_name, :service_date, :tags, :creator_id) "
            "RETURNING id, leader_name, service_date, tags, created_on, creator_id",
            request_body.model_dump()
            | {"creator_id": session_user(bp.current_request).id},
            output=Setlist,
        )
        setlist = curs.fetchone()
        assert setlist is not None

    return setlist


@bp.route("/setlists/{setlist_id}", methods=["GET"])
def get_setlist(setlist_id: str) -> Forbidden | NotFound | Setlist:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, leader_name, service_date, tags, created_on, creator_id "
            "FROM setlists WHERE id = :setlist_id",
            {"setlist_id": setlist_id},
            output=Setlist,
        )
        setlist = curs.fetchone()
        return setlist if setlist is not None else NotFound()


@bp.route("/setlists/{setlist_id}", methods=["PUT"])
def update_setlist(
    setlist_id: str, request_body: UpdateSetlist
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE setlists SET {request_body.replacement_sql} WHERE id = :id",
            {"id": setlist_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/setlists/{setlist_id}", methods=["DELETE"])
def delete_setlist(setlist_id: str) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute("DELETE FROM setlists WHERE id = :id", {"id": setlist_id})
        return NoContent() if result else NotFound()


@bp.route("/setlists/{setlist_id}/pos", methods=["GET"])
def list_setlist_positions(setlist_id: str) -> Forbidden | SetlistPositionList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, setlist_id, index, label, is_music, presenter, status "
            "FROM setlist_positions WHERE setlist_id = :setlist_id "
            "ORDER BY index",
            {"setlist_id": setlist_id},
            output=SetlistPosition,
        )
        return SetlistPositionList(positions=curs.fetchall())


@bp.route("/setlists/{setlist_id}/pos", methods=["POST"])
def new_setlist_position(
    setlist_id: str, request_body: NewSetlistPosition
) -> Forbidden | SetlistPosition:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO setlist_positions ("
            "    setlist_id, index, label, is_music, presenter, status"
            ") VALUES ("
            "    :setlist_id, :index, :label, :is_music, :presenter, :status"
            ") "
            "RETURNING id, setlist_id, index, label, is_music, presenter, status",
            request_body.model_dump() | {"setlist_id": setlist_id},
            output=SetlistPosition,
        )
        setlist_position = curs.fetchone()
        assert setlist_position is not None

    return setlist_position


@bp.route("/setlists/{setlist_id}/pos/{position_id}", methods=["GET"])
def get_setlist_position(
    setlist_id: str, position_id: str
) -> Forbidden | NotFound | SetlistPosition:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  id, setlist_id, index, label, is_music, presenter, status "
            "FROM setlist_positions "
            "WHERE id = :position_id AND setlist_id = :setlist_id",
            {"position_id": position_id, "setlist_id": setlist_id},
            output=SetlistPosition,
        )
        setlist_position = curs.fetchone()
        return setlist_position if setlist_position is not None else NotFound()


@bp.route("/setlists/{setlist_id}/pos/{position_id}", methods=["PUT"])
def update_setlist_position(
    setlist_id: str, position_id: str, request_body: UpdateSetlistPosition
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE setlist_positions SET {request_body.replacement_sql} "
            f"WHERE id = :position_id AND setlist_id = :setlist_id",
            {"position_id": position_id, "setlist_id": setlist_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/setlists/{setlist_id}/pos/{position_id}", methods=["DELETE"])
def delete_setlist_position(
    setlist_id: str, position_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM setlist_positions "
            "WHERE id = :position_id AND setlist_id = :setlist_id",
            {"position_id": position_id, "setlist_id": setlist_id},
        )
        return NoContent() if result else NotFound()


@bp.route("/setlists/{setlist_id}/sheets", methods=["GET"])
def list_setlist_sheets(setlist_id: str) -> Forbidden | SetlistSheetList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  setlist_sheets.id,"
            "  setlist_sheets.setlist_id,"
            "  setlist_sheets.type,"
            "  setlist_sheets.song_sheet_id,"
            "  setlist_sheets.setlist_position_id,"
            "  song_versions.id AS song_version_id, "
            "  song_versions.song_id AS song_id "
            "FROM setlist_sheets "
            "INNER JOIN song_sheets ON song_sheets.id = setlist_sheets.song_sheet_id "
            "INNER JOIN song_versions ON"
            "  song_versions.id = song_sheets.song_version_id "
            "WHERE setlist_sheets.setlist_id = :setlist_id "
            "ORDER BY setlist_sheets.type",
            {"setlist_id": setlist_id},
            output=SetlistSheet,
        )
        return SetlistSheetList(sheets=curs.fetchall())


@bp.route("/setlists/{setlist_id}/sheets", methods=["POST"])
def new_setlist_sheet(
    setlist_id: str, request_body: NewSetlistSheet
) -> Forbidden | SetlistSheet:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO setlist_sheets ("
            "  setlist_id, type, song_sheet_id, setlist_position_id"
            ") VALUES ("
            "  :setlist_id, :type, :song_sheet_id, :setlist_position_id"
            ") "
            "RETURNING id, setlist_id, type, song_sheet_id, setlist_position_id,"
            "  '' AS song_version_id, '' AS song_id",
            request_body.model_dump() | {"setlist_id": setlist_id},
            output=SetlistSheet,
        )
        sheet = curs.fetchone()
        assert sheet is not None

    return sheet


@bp.route("/setlists/{setlist_id}/sheets/{sheet_id}", methods=["GET"])
def get_setlist_sheet(
    setlist_id: str, sheet_id: str
) -> Forbidden | NotFound | SetlistSheet:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT"
            "  setlist_sheets.id,"
            "  setlist_sheets.setlist_id,"
            "  setlist_sheets.type,"
            "  setlist_sheets.song_sheet_id,"
            "  setlist_sheets.setlist_position_id,"
            "  song_versions.id AS song_version_id, "
            "  song_versions.song_id AS song_id "
            "FROM setlist_sheets "
            "INNER JOIN song_sheets ON song_sheets.id = setlist_sheets.song_sheet_id "
            "INNER JOIN song_versions ON"
            "  song_versions.id = song_sheets.song_version_id "
            "WHERE setlist_sheets.setlist_id = :setlist_id"
            "  AND setlist_sheets.id = :sheet_id",
            {"sheet_id": sheet_id, "setlist_id": setlist_id},
            output=SetlistSheet,
        )
        sheet = curs.fetchone()
        return sheet if sheet is not None else NotFound()


@bp.route("/setlists/{setlist_id}/sheets/{sheet_id}", methods=["PUT"])
def update_setlist_sheet(
    setlist_id: str, sheet_id: str, request_body: UpdateSetlistSheet
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE setlist_sheets SET {request_body.replacement_sql} "
            f"WHERE id = :sheet_id AND setlist_id = :setlist_id",
            {"sheet_id": sheet_id, "setlist_id": setlist_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/setlists/{setlist_id}/sheets/{sheet_id}", methods=["DELETE"])
def delete_setlist_sheet(
    setlist_id: str, sheet_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM setlist_sheets "
            "WHERE id = :sheet_id AND setlist_id = :setlist_id",
            {"sheet_id": sheet_id, "setlist_id": setlist_id},
        )
        return NoContent() if result else NotFound()


@bp.route("/setlistTemplates", methods=["GET"])
def list_setlist_templates() -> Forbidden | SetlistTemplateList:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, title, tags, created_on, creator_id FROM setlist_templates "
            "ORDER BY title",
            output=SetlistTemplate,
        )
        return SetlistTemplateList(templates=curs.fetchall())


@bp.route("/setlistTemplates", methods=["POST"])
def new_setlist_template(
    request_body: NewSetlistTemplate,
) -> Forbidden | SetlistTemplate:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO setlist_templates (title, tags, creator_id) "
            "VALUES (:title, :tags, :creator_id) "
            "RETURNING id, title, tags, created_on, creator_id",
            request_body.model_dump()
            | {"creator_id": session_user(bp.current_request).id},
            output=SetlistTemplate,
        )
        template = curs.fetchone()
        assert template is not None

    return template


@bp.route("/setlistTemplates/{template_id}", methods=["GET"])
def get_setlist_template(template_id: str) -> Forbidden | NotFound | SetlistTemplate:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, title, tags, created_on, creator_id "
            "FROM setlist_templates WHERE id = :template_id",
            {"template_id": template_id},
            output=SetlistTemplate,
        )
        template = curs.fetchone()
        return template if template is not None else NotFound()


@bp.route("/setlistTemplates/{template_id}", methods=["PUT"])
def update_setlist_template(
    template_id: str, request_body: UpdateSetlistTemplate
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE setlist_templates SET {request_body.replacement_sql} "
            f"WHERE id = :id",
            {"id": template_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/setlistTemplates/{template_id}", methods=["DELETE"])
def delete_setlist_template(template_id: str) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM setlist_templates WHERE id = :id", {"id": template_id}
        )
        return NoContent() if result else NotFound()


@bp.route("/setlistTemplates/{template_id}/pos", methods=["GET"])
def list_setlist_template_positions(
    template_id: str,
) -> Forbidden | SetlistTemplatePositionList:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, template_id, index, label, is_music, presenter "
            "FROM setlist_template_positions WHERE template_id = :template_id "
            "ORDER BY index",
            {"template_id": template_id},
            output=SetlistTemplatePosition,
        )
        return SetlistTemplatePositionList(positions=curs.fetchall())


@bp.route("/setlistTemplates/{template_id}/pos", methods=["POST"])
def new_setlist_template_position(
    template_id: str, request_body: NewSetlistTemplatePosition
) -> Forbidden | SetlistTemplatePosition:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO setlist_template_positions ("
            "  template_id, index, label, is_music, presenter"
            ") VALUES ("
            "  :template_id, :index, :label, :is_music, :presenter"
            ") "
            "RETURNING id, template_id, index, label, is_music, presenter",
            request_body.model_dump() | {"template_id": template_id},
            output=SetlistTemplatePosition,
        )
        template_position = curs.fetchone()
        assert template_position is not None

    return template_position


@bp.route("/setlistTemplates/{template_id}/pos/{position_id}", methods=["GET"])
def get_setlist_template_position(
    template_id: str, position_id: str
) -> Forbidden | NotFound | SetlistTemplatePosition:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, template_id, index, label, is_music, presenter "
            "FROM setlist_template_positions "
            "WHERE id = :position_id AND template_id = :template_id",
            {"position_id": position_id, "template_id": template_id},
            output=SetlistTemplatePosition,
        )
        template_position = curs.fetchone()
        return template_position if template_position is not None else NotFound()


@bp.route("/setlistTemplates/{template_id}/pos/{position_id}", methods=["PUT"])
def update_setlist_template_position(
    template_id: str, position_id: str, request_body: UpdateSetlistTemplatePosition
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    if not request_body.any_replacements:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE setlist_template_positions SET {request_body.replacement_sql} "
            f"WHERE id = :position_id AND template_id = :template_id",
            {"position_id": position_id, "template_id": template_id}
            | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/setlistTemplates/{template_id}/pos/{position_id}", methods=["DELETE"])
def delete_setlist_template_position(
    template_id: str, position_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM setlist_template_positions "
            "WHERE id = :position_id AND template_id = :template_id",
            {"position_id": position_id, "template_id": template_id},
        )
        return NoContent() if result else NotFound()
