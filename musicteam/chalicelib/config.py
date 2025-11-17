# app-wide configuration settings
#
import base64
import os
import random
import sys

import boto3

secretsmanager = boto3.client("secretsmanager")

INSTANCE_DIR = "../instance"

IS_CHALICE_LOCAL = sys.argv[0].endswith("chalice")

try:
    SITE_SECRET = os.environ["SITE_SECRET"]
except KeyError:
    print("WARNING -- SITE_SECRET not provided, using a randomly generated key...")
    SITE_SECRET = base64.b64encode(random.randbytes(32)).decode()

if SITE_SECRET.startswith("arn:aws:secretsmanager"):
    # retrieve the secret value from Secrets Manager
    SITE_SECRET = secretsmanager.get_secret_value(SecretId=SITE_SECRET)["SecretString"]

OBJECT_BUCKET_NAME = os.environ.get("OBJECT_BUCKET_NAME", "local")

OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", "")

if OAUTH_CLIENT_SECRET.startswith("arn:aws:secretsmanager"):
    OAUTH_CLIENT_SECRET = secretsmanager.get_secret_value(SecretId=OAUTH_CLIENT_SECRET)[
        "SecretString"
    ]

AURORA_CLUSTER_ARN = os.environ.get("AURORA_CLUSTER_ARN")
AURORA_SECRET_ARN = os.environ.get("AURORA_SECRET_ARN")
