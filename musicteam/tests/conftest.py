from json import dumps
from typing import Any

import pytest
from app import app
from chalice.test import Client
from chalicelib import db as app_db


@pytest.fixture
def db(monkeypatch, tmp_path):
    monkeypatch.setattr(app_db, "INSTANCE_DIR", str(tmp_path))
    yield app_db


@pytest.fixture
def client(monkeypatch, db):
    monkeypatch.setattr(app_db, "ping", lambda: True)
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
            if json is not None:
                if headers is None:
                    headers = {}
                headers["Content-Type"] = "application/json"
                body = dumps(json).encode()
            return original_request(method, path, headers=headers, body=body)

        client.http.request = request

        yield client
