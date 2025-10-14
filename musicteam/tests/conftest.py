from types import MethodType
from typing import Any
from json import dumps

from chalice.test import Client, TestHTTPClient
import pytest

from app import app
from chalicelib import db


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(db, "ping", lambda: True)
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
