FROM python:3.13-slim

RUN apt update \
        && apt install -y git curl libpq-dev unzip \
        && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
        && apt install -y nodejs \
        && curl -L https://github.com/pgsty/silo/releases/download/RELEASE.2026-02-14T12-00-00Z/minio_20260214120000.0.0_$(dpkg --print-architecture).deb -o /tmp/minio.deb \
        && dpkg -i /tmp/minio.deb && rm /tmp/minio.deb \
        && apt autoremove -y \
        && apt autoclean -y

COPY ./requirements-dev.txt /srv/musicteam/
COPY ./musicteam/requirements.txt ./musicteam/requirements-semantic.txt /srv/musicteam/musicteam/

WORKDIR /srv/musicteam

RUN pip install -r requirements-dev.txt -r musicteam/requirements.txt -r musicteam/requirements-semantic.txt

COPY ./musicteam-nuxt/package.json ./musicteam-nuxt/get-pdfjs.sh /srv/musicteam/musicteam-nuxt/

RUN cd musicteam-nuxt && npm install

COPY . /srv/musicteam

ENV AWS_DEFAULT_REGION=us-east-1

RUN cd musicteam && python -m chalicelib.semantic fetch

EXPOSE 8000 3000

CMD ["./start-dev.sh"]
