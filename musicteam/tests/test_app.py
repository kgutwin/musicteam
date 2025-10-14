import json

from chalice.test import Client
from app import app


def test_modeled_body(client):
    response = client.http.post("/names/flarb", json={"count": 4})
    assert response.json_body == {"count": 4}
