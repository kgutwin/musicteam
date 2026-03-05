import re
from io import BytesIO
from json import dumps
from typing import Any

import pytest
from app import app
from chalice.test import Client
from chalicelib import db as app_db
from chalicelib.types import User
from syrupy.extensions.single_file import SingleFileSnapshotExtension


@pytest.fixture
def db(monkeypatch, tmp_path):
    monkeypatch.setattr(app_db, "PGLITE_MANAGER", None)
    monkeypatch.setattr(app_db, "INSTANCE_DIR", str(tmp_path))
    yield app_db


@pytest.fixture
def client(monkeypatch, db):
    token = User(
        id="u:41c95da1-7eaf-4d0f-8669-6df165204d6c",
        name="Pytest",
        provider_id="pytest",
        email="",
        role="admin",
    ).to_token()

    db.ping()
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO users (id, name, provider_id, role) "
            "VALUES ("
            "  'u:41c95da1-7eaf-4d0f-8669-6df165204d6c', 'Pytest', 'pytest', 'admin'"
            ")"
        )

    with Client(app) as client:
        # add a json kwarg to client request
        original_request = client.http.request

        def request(
            method: str,
            path: str,
            headers: dict[str, str] | None = None,
            body: bytes = b"",
            json: dict[str, str] | None = None,
        ) -> Any:
            if headers is None:
                headers = {}
            headers["Cookie"] = f"session={token}"

            if json is not None:
                headers["Content-Type"] = "application/json"
                body = dumps(json).encode()

            return original_request(method, path, headers=headers, body=body)

        client.http.request = request

        yield client


@pytest.fixture
def mock_storage(monkeypatch):
    from chalicelib import storage

    class MockS3:
        def __init__(self):
            self.data = {}

        def get_object(self, Bucket, Key):
            assert Key in self.data, f"must register {Key} in mock data"
            return {"Body": BytesIO(self.data[Key])}

        def head_object(self, Bucket, Key):
            assert Key in self.data, f"must register {Key} in mock data"
            return {"ContentLength": 12345}

        def put_object(self, Bucket, Key, Body):
            self.data[Key] = Body

    mock_s3 = MockS3()

    monkeypatch.setattr(storage, "s3", mock_s3)

    yield mock_s3


class PDFSnapshotExtension(SingleFileSnapshotExtension):
    STATIC_ID = (
        b"/ID[<C29E67C3AFC39BC289C28116217BC2AA><D4C7CDFF2AE8F6901B146F8FCBA86701>]"
    )
    file_extension = "pdf"

    def serialize(self, data, **kwargs):
        return re.sub(rb"/ID\[[^]]+\]", self.STATIC_ID, data)


@pytest.fixture
def pdf_snapshot(snapshot):
    return snapshot.use_extension(PDFSnapshotExtension)
