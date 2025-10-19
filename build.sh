#!/bin/sh

set -e

if [[ ! -d venv ]]; then
    python3.13 -m venv venv
    . venv/bin/activate
    pip install -r requirements-dev.txt
    pip install -r musicteam/requirements.txt
else
    . venv/bin/activate
fi

if [[ -f .env ]]; then . .env; fi

rm -rf deploy

pushd musicteam
mypy app.py --strict

chalice package \
        --template-format yaml \
        --merge-template ../cfn.yaml \
        ../deploy
popd

aws cloudformation package \
    --template-file deploy/sam.yaml \
    --s3-bucket $AWS_DEPLOY_S3_BUCKET \
    --output-template-file deploy/packaged.yaml

aws cloudformation deploy \
    --template-file deploy/packaged.yaml \
    --stack-name musicteam \
    --parameter-overrides VpcId=$AWS_VPC PrivateSubnets=$AWS_SUBNETS \
    --capabilities CAPABILITY_IAM
