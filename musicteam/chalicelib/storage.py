import os
import sys

import boto3

BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
if BUCKET_NAME == "local" and sys.argv[0].endswith("chalice"):
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
        s3.create_bucket(Bucket=BUCKET_NAME)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass

else:
    s3 = boto3.client("s3")
