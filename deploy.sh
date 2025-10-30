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

# Frontend build
pushd musicteam-nuxt
npm run generate
popd

# Backend build
pushd musicteam
mypy app.py --strict

chalice package \
        --template-format yaml \
        --merge-template ../cfn.yaml \
        ../deploy
popd

# Deploy

aws cloudformation package \
    --template-file deploy/sam.yaml \
    --s3-bucket $AWS_DEPLOY_S3_BUCKET \
    --output-template-file deploy/packaged.yaml

aws cloudformation deploy \
    --template-file deploy/packaged.yaml \
    --s3-bucket $AWS_DEPLOY_S3_BUCKET \
    --stack-name musicteam \
    --parameter-overrides \
    VpcId=$AWS_VPC \
    PrivateSubnets=$AWS_SUBNETS \
    FQDN=$AWS_FQDN \
    HostedZoneId=$AWS_HOSTED_ZONE_ID \
    OAuthClientId=$OAUTH_CLIENT_ID \
    OAuthClientSecret=$OAUTH_CLIENT_SECRET \
    --capabilities CAPABILITY_IAM

# Upload frontend package

aws s3 sync --delete musicteam-nuxt/.output/public s3://musicteam-frontend/
