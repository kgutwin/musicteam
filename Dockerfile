FROM python:3.13-alpine

RUN apk add --no-cache build-base linux-headers minio nodejs npm git libpq-dev

COPY . /srv/musicteam
WORKDIR /srv/musicteam

RUN pip install -r requirements-dev.txt -r musicteam/requirements.txt

RUN cd musicteam-nuxt && npm install

ENV AWS_DEFAULT_REGION=us-east-1

EXPOSE 8000 3000

CMD ["./start-dev.sh"]
