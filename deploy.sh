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

# Jump through some hoops to get pymupdf, since chalice is being unhelpful for
# just this one package
mkdir -p vendor
TMPD=$(mktemp -d)
pip download --only-binary=:all: --no-deps --platform manylinux_2_28_x86_64 \
    --implementation cp --abi cp313 --dest $TMPD pymupdf
pushd vendor
rm -rf fitz pymupdf*
unzip $TMPD/pymupdf*.whl
popd
rm -rf $TMPD

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
