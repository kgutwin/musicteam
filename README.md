# MusicTeam - organize and share music for your team

## Quickstart

For a quick test of the app, you can run it fully in Docker:

```
docker buildx build -t musicteam .
docker run -d -p 3000:3000 musicteam
```

and visit http://localhost:3000/ .

Note that when running locally, by default the Google user login will be bypassed.

## Architecture

The backend of MusicTeam is built using
[Chalice](https://github.com/aws/chalice) to run on top of AWS Lambda.
All metadata is stored in Amazon Aurora Serverless PostgreSQL, and
uploaded data is stored in Amazon S3. The frontend is built using
[Nuxt 4](https://nuxt.com)/[Vue3](https://vuejs.org), with static site
generation, served out via Amazon CloudFront. Configuration and
deployment is handled via CloudFormation.

## Setting up a Development Environment

As prerequisites, you will need:

- Python 3.13
- NodeJS v22+
- The MinIO server (https://github.com/minio/minio)

### Backend Development

Set up your Python virtual environment:

```bash
python3.13 -m venv venv
. venv/bin/activate

pip install -r requirements-dev.txt -r musicteam/requirements.txt
```

Then you can use `chalice local` to run the stack locally:

```bash
cd musicteam
chalice local
```

It will auto reload on any changes to Python scripts under the
`musicteam` directory. All uploaded content will be stored in the
`instance/` directory at the top of the repository.

NOTE: if you want to avoid losing user sessions on every code refresh,
try setting the `SITE_SECRET` environment variable to a value of your
choosing:

```bash
SITE_SECRET=myinsecurevalue chalice local
```

### Frontend Development

Use `npm` to install all necessary packages:

```bash
cd musicteam-nuxt
npm install
```

Then, start the Nuxt dev server:

```bash
npm run dev -- -o
```

If you want, you can point your development frontend at a running
backend instance of MusicTeam via an environment variable.

```bash
REMOTE_API=musicteam.example.com npm run dev
```

### Pre-commit

This project uses [pre-commit](https://pre-commit.com) to help manage
code consistency. Before creating any commits, you should install the
pre-commit hooks into your local clone of the repo:

```bash
# activate your virtual environment if needed
. venv/bin/activate

pre-commit install
```

## Deployment

You can deploy an instance of the MusicTeam stack using the
`deploy.sh` script. You will need to create a `.env` file with some
essential values:

```
AWS_DEPLOY_S3_BUCKET=mybucket  # name of a bucket to hold deployments for CloudFormation
AWS_VPC=vpc-a1b2c3d4           # VPC ID
AWS_SUBNETS=subnet-aabb,...    # At least three private subnet IDs for Aurora
AWS_FQDN=mt.example.com        # Your app's final domain name in Route 53
AWS_HOSTED_ZONE_ID=Z0123...    # The hosted zone ID of your Route 53 zone

OAUTH_CLIENT_ID=xxxx           # Create a Google OAuth client using the steps at:
OAUTH_CLIENT_SECRET=yyyy       # https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid
```
