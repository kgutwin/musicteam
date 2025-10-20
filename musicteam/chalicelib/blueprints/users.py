from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.types import Forbidden
from chalicelib.types import NotFound
from chalicelib.types import User
from chalicelib.types import UserList

bp = Blueprint(__name__)


@bp.route("/users", methods=["GET"])
def list_users() -> Forbidden | UserList:
    if not session_role(bp.current_request, "manager"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, name, provider_id, email, picture, role FROM users",
            output=User,
        )
        return UserList(users=curs.fetchall())


@bp.route("/users/{user_id}", methods=["GET"])
def get_user(user_id: str) -> Forbidden | NotFound | User:
    if not session_role(bp.current_request, "manager"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, name, provider_id, email, picture, role FROM users "
            "WHERE id = :id",
            {"id": user_id},
            output=User,
        )
        user = curs.fetchone()
        return user if user is not None else NotFound()
