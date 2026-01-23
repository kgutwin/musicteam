from json import dumps
from typing import Any

import pytest
from app import app
from chalice.test import Client
from chalicelib import db as app_db
from chalicelib.types import User


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
