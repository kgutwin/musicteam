import base64
import uuid

from chalice.app import Blueprint
from chalicelib.config import OBJECT_BUCKET_NAME
from chalicelib.middleware import session_role
from chalicelib.storage import s3
from chalicelib.types import Forbidden
from chalicelib.types import ObjectId
from chalicelib.types import UploadDirect
from chalicelib.types import UploadParams

bp = Blueprint(__name__)


@bp.route("/objects", methods=["POST"], content_types=["text/plain"])
def upload_file(
    request_body: bytes, query_params: UploadParams
) -> Forbidden | ObjectId:
    """Upload a file (object) to the site

    Limited to objects smaller than ~5 MB.

    If the `base64` field is True, then the request body will be
    decoded from Base64 before storage.

    """
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    object_id = str(uuid.uuid4())

    if query_params.base64:
        request_body = base64.b64decode(request_body)

    s3.put_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id, Body=request_body)

    return ObjectId(id=object_id)


@bp.route("/objects/direct", methods=["POST"])
def upload_file_direct() -> Forbidden | UploadDirect:
    """Upload a file (object) directly to the site's underlying storage"""
    if not session_role(bp.current_request, "leader"):
        return Forbidden()

    object_id = str(uuid.uuid4())

    response = s3.generate_presigned_post(OBJECT_BUCKET_NAME, object_id)

    return UploadDirect(url=response["url"], fields=response["fields"])
