import random
import string

from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.middleware import session_user
from chalicelib.types import BadRequest
from chalicelib.types import Forbidden
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import UpdateUser
from chalicelib.types import User
from chalicelib.types import UserApikey
from chalicelib.types import UserList

bp = Blueprint(__name__)


@bp.route("/users", methods=["GET"])
def list_users() -> Forbidden | UserList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, name, provider_id, email, picture, role FROM users "
            "ORDER BY name",
            output=User,
        )
        return UserList(users=curs.fetchall())


@bp.route("/users/{user_id}", methods=["GET"])
def get_user(user_id: str) -> Forbidden | NotFound | User:
    if not (
        user_id == session_user(bp.current_request).id
        or session_role(bp.current_request, "viewer")
    ):
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


@bp.route("/users/{user_id}", methods=["PUT"])
def update_user(
    user_id: str, request_body: UpdateUser
) -> Forbidden | NotFound | NoContent:
    if not (
        user_id == session_user(bp.current_request).id
        or session_role(bp.current_request, "manager")
    ):
        return Forbidden("Not a manager")

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, name, provider_id, email, picture, role FROM users "
            "WHERE id = :id",
            {"id": user_id},
            output=User,
        )
        user = curs.fetchone()
        if user is None:
            return NotFound()

    # don't allow users to update their own role
    if (
        not session_role(bp.current_request, "manager")
        and request_body.role != user.role
    ):
        return Forbidden("Cannot update own role")

    with db.connect() as conn:
        result = conn.execute(
            f"UPDATE users SET {request_body.replacement_sql} WHERE id = :id",
            {"id": user_id} | request_body.replacement_params,
        )
        return NoContent() if result else NotFound()


@bp.route("/users/{user_id}/apikey", methods=["POST"])
def create_user_apikey(user_id: str) -> Forbidden | BadRequest | NotFound | UserApikey:
    if user_id != session_user(bp.current_request).id:
        return Forbidden()
    if session_user(bp.current_request).api_key:
        return BadRequest("Cannot create a new API key using an API key")

    with db.connect() as conn:
        new_key = "".join(random.choices(string.ascii_uppercase + string.digits, k=18))
        curs = conn.execute(
            "UPDATE users SET api_key = :new_key WHERE id = :id",
            {"id": user_id, "new_key": new_key},
        )
        if curs == 0:
            return NotFound()

    return UserApikey(api_key=new_key)
