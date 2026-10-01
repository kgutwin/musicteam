import pytest


@pytest.fixture
def resources(client):
    response = client.http.post(
        "/songs",
        json={
            "title": "x",
            "authors": [],
            "ccli_num": None,
            "tags": ["song-x", "song-y", "pytest"],
        },
    )
    assert response.status_code == 200, response.body
    response = client.http.post(
        "/songs",
        json={
            "title": "y",
            "authors": [],
            "ccli_num": None,
            "tags": ["song-x", "song-z"],
        },
    )
    assert response.status_code == 200, response.body

    response = client.http.post(
        "/setlists",
        json={
            "leader_name": "joe",
            "service_date": "2026-01-25",
            "tags": ["setlist-x", "pytest"],
        },
    )
    assert response.status_code == 200, response.body


def test_list_tags(client, resources):
    response = client.http.get("/info/tags")
    assert response.json_body["entries"] == [
        {"entry": "pytest", "count": 2},
        {"entry": "setlist-x", "count": 1},
        {"entry": "song-x", "count": 2},
        {"entry": "song-y", "count": 1},
        {"entry": "song-z", "count": 1},
    ]


def test_list_tags_by_resource_type(client, resources):
    response = client.http.get("/info/tags/songs")
    assert response.json_body["entries"] == [
        {"entry": "pytest", "count": 1},
        {"entry": "song-x", "count": 2},
        {"entry": "song-y", "count": 1},
        {"entry": "song-z", "count": 1},
    ]

    response = client.http.get("/info/tags/setlists")
    assert response.json_body["entries"] == [
        {"entry": "pytest", "count": 1},
        {"entry": "setlist-x", "count": 1},
    ]

    response = client.http.get("/info/tags/setlist_templates")
    assert response.json_body["entries"] == []
