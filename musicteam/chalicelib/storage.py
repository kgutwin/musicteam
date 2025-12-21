import os
import sys
from io import RawIOBase
from typing import cast

import boto3
from chalicelib.config import IS_CHALICE_LOCAL
from chalicelib.config import OBJECT_BUCKET_NAME
from chalicelib.types import Download
from chalicelib.types import Found
from chalicelib.types import PartialDownload

if OBJECT_BUCKET_NAME == "local" and IS_CHALICE_LOCAL and sys.argv[-1] == "local":
    import os
    import atexit
    import shutil
    import subprocess
    import botocore.client

    minio_endpoint_url = "http://127.0.0.1:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    object_dir = "../instance/objects"

    os.makedirs(object_dir, exist_ok=True)

    minio_path = shutil.which("minio")
    assert minio_path is not None, "Minio not found!"
    minio = subprocess.Popen([minio_path, "server", object_dir])
    atexit.register(minio.kill)

    s3 = boto3.client(
        "s3",
        endpoint_url=minio_endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=botocore.client.Config(signature_version="s3v4"),
    )

    try:
        s3.create_bucket(Bucket=OBJECT_BUCKET_NAME)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass

else:
    s3 = boto3.client("s3")


def get(object_id: str) -> RawIOBase:
    resp = s3.get_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id)
    return cast(RawIOBase, resp["Body"])


def get_download(
    object_id: str,
    content_type: str,
    head: bool = False,
    range_req: str | None = None,
) -> Download | PartialDownload | Found:
    s3_resp = s3.head_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id)

    if head:
        return Download(
            b"",
            headers={
                "Content-Type": content_type,
                "Accept-Ranges": "bytes",
                "Content-Length": str(s3_resp["ContentLength"]),
            },
        )

    if s3_resp["ContentLength"] > 3_500_000:
        response = s3.generate_presigned_url(
            "get_object", Params={"Bucket": OBJECT_BUCKET_NAME, "Key": object_id}
        )
        return Found(response)

    extra: dict[str, str] = {}
    if range_req:
        extra["Range"] = range_req

    s3_resp = s3.get_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id, **extra)

    headers: dict[str, str | list[str]] = {
        "Content-Type": content_type,
    }
    body = s3_resp["Body"].read()
    if content_type == "text/plain":
        # if we uploaded a file which can't be read as utf-8, then
        # chalice is going to have problems with it, so replace bad
        # bytes with the unknown character.
        body = body.decode(errors="replace").encode()

    if range_req:
        headers["Content-Range"] = s3_resp["ContentRange"]
        return PartialDownload(body, headers=headers)
    else:
        return Download(body, headers=headers)
