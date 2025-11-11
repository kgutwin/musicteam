from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.types import Entry
from chalicelib.types import EntryList
from chalicelib.types import Forbidden

bp = Blueprint(__name__)


@bp.route("/info/tags", methods=["GET"])
def list_tags() -> Forbidden | EntryList:
    """List all tags in the system, across songs, setlists, etc"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute("SELECT tag AS entry, count FROM all_tags", output=Entry)
        return EntryList(entries=curs.fetchall())


@bp.route("/info/authors", methods=["GET"])
def list_authors() -> Forbidden | EntryList:
    """List all song authors"""
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT author AS entry, count FROM all_authors", output=Entry
        )
        return EntryList(entries=curs.fetchall())
