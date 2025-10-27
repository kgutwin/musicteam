import base64
import uuid

from chalice.app import Blueprint
from chalicelib.middleware import session_role
from chalicelib.storage import BUCKET_NAME
from chalicelib.storage import s3
from chalicelib.types import Forbidden
from chalicelib.types import ObjectId
from chalicelib.types import UploadParams

bp = Blueprint(__name__)


@bp.route("/objects", methods=["POST"], content_types=["text/plain"])
def upload_file(
    request_body: bytes, query_params: UploadParams
) -> Forbidden | ObjectId:
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    object_id = str(uuid.uuid4())

    if query_params.base64:
        request_body = base64.b64decode(request_body)

    s3.put_object(Bucket=BUCKET_NAME, Key=object_id, Body=request_body)

    return ObjectId(id=object_id)
