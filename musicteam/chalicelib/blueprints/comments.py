from chalice.app import Blueprint
from chalicelib import db
from chalicelib.middleware import session_role
from chalicelib.middleware import session_user
from chalicelib.types import Comment
from chalicelib.types import CommentList
from chalicelib.types import Forbidden
from chalicelib.types import NewComment
from chalicelib.types import NoContent
from chalicelib.types import NotFound
from chalicelib.types import UpdateComment

bp = Blueprint(__name__)


@bp.route("/comments/{resource_id}", methods=["GET"])
def list_comments(resource_id: str) -> Forbidden | CommentList:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, resource_id, comment, created_on, creator_id "
            "FROM comments "
            "WHERE resource_id = :resource_id "
            "ORDER BY created_on",
            output=Comment,
        )
        return CommentList(comments=curs.fetchall())


@bp.route("/comments/{resource_id}", methods=["POST"])
def new_comment(resource_id: str, request_body: NewComment) -> Forbidden | Comment:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "INSERT INTO comments (resource_id, comment, creator_id) "
            "VALUES (:resource_id, :comment, :creator_id) "
            "RETURNING id, resource_id, comment, created_on, creator_id",
            {
                "resource_id": resource_id,
                "comment": request_body.comment,
                "creator_id": session_user(bp.current_request).id,
            },
            output=Comment,
        )
        comment = curs.fetchone()
        assert comment is not None

    return comment


@bp.route("/comments/{resource_id}/{comment_id}", methods=["GET"])
def get_comment(resource_id: str, comment_id: str) -> Forbidden | NotFound | Comment:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        curs = conn.execute(
            "SELECT id, resource_id, comment, created_on, creator_id "
            "FROM comments WHERE id = :comment_id AND resource_id = :resource_id",
            {"comment_id": comment_id, "resource_id": resource_id},
            output=Comment,
        )
        comment = curs.fetchone()
        return comment if comment is not None else NotFound()


@bp.route("/comments/{resource_id}/{comment_id}", methods=["PUT"])
def update_comment(
    resource_id: str, comment_id: str, request_body: UpdateComment
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    if request_body.comment is None:
        return NoContent()

    with db.connect() as conn:
        result = conn.execute(
            "UPDATE comments SET comment = :comment "
            "WHERE id = :comment_id AND resource_id = :resource_id"
            "  AND creator_id = :creator_id",
            {
                "comment_id": comment_id,
                "comment": request_body.comment,
                "resource_id": resource_id,
                "creator_id": session_user(bp.current_request).id,
            },
        )
        return NoContent() if result else NotFound()


@bp.route("/comments/{resource_id}/{comment_id}", methods=["DELETE"])
def delete_comment(
    resource_id: str, comment_id: str
) -> Forbidden | NotFound | NoContent:
    if not session_role(bp.current_request, "viewer"):
        return Forbidden()

    with db.connect() as conn:
        result = conn.execute(
            "DELETE FROM comments "
            "WHERE id = :comment_id AND resource_id = :resource_id"
            "  AND creator_id = :creator_id",
            {
                "comment_id": comment_id,
                "resource_id": resource_id,
                "creator_id": session_user(bp.current_request).id,
            },
        )
        return NoContent() if result else NotFound()
