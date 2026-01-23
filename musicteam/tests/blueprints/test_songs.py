def test_songs_get(client):
    response = client.http.get("/songs")
    assert response.json_body == {"songs": []}


def test_songs_new(client):
    response = client.http.post(
        "/songs",
        json={
            "title": "test song",
            "authors": ["foo", "bar"],
            "ccli_num": 12345,
            "tags": ["pytest"],
        },
    )
    assert response.json_body["title"] == "test song"


def test_songs_update_delete(client):
    response = client.http.post(
        "/songs",
        json={
            "title": "test song",
            "authors": ["foo", "bar"],
            "ccli_num": 12345,
            "tags": ["pytest"],
        },
    )
    song_id = response.json_body["id"]

    response = client.http.put(f"/songs/{song_id}", json={"title": "new song"})
    assert response.status_code == 204

    response = client.http.get(f"/songs/{song_id}/revisions")
    assert response.status_code == 200
    revs = response.json_body["song_revisions"]

    assert len(revs) == 1
    assert revs[0]["title"] == "test song"
    assert revs[0]["id"] == song_id
    assert revs[0]["rev_changed_by"] == "u:41c95da1-7eaf-4d0f-8669-6df165204d6c"

    response = client.http.delete(f"/songs/{song_id}")
    assert response.status_code == 204

    response = client.http.get(f"/songs/{song_id}")
    assert response.status_code == 404

    response = client.http.get(f"/songs/{song_id}/revisions")
    assert response.status_code == 200
    revs = response.json_body["song_revisions"]

    assert len(revs) == 2
    assert revs[0]["title"] == "new song"


def test_song_version_sheet_update_delete(client, db):
    response = client.http.post(
        "/songs",
        json={
            "title": "test song",
            "authors": ["foo", "bar"],
            "ccli_num": 12345,
            "tags": ["pytest"],
        },
    )
    song_id = response.json_body["id"]

    response = client.http.post(
        f"/songs/{song_id}/versions", json={"label": "from foo"}
    )
    assert response.status_code == 200
    song_version_id = response.json_body["id"]

    response = client.http.post(
        f"/songs/{song_id}/versions/{song_version_id}/sheets",
        json={
            "type": "Chord",
            "key": "D",
            "object_id": "xyz",
            "object_type": "text/plain",
        },
    )
    assert response.status_code == 200
    song_sheet_id = response.json_body["id"]

    # change version
    response = client.http.put(
        f"/songs/{song_id}/versions/{song_version_id}", json={"label": "From Foo"}
    )
    assert response.status_code == 204

    # change sheet
    response = client.http.put(
        f"/songs/{song_id}/versions/{song_version_id}/sheets/{song_sheet_id}",
        json={"type": "Lead", "key": "C"},
    )
    assert response.status_code == 204

    response = client.http.get(f"/songs/{song_id}/revisions")
    assert response.status_code == 200
    revs = response.json_body["song_revisions"]

    assert len(revs) == 2
    assert revs[0]["rev_type"] == "song_sheet"
    assert revs[0]["type"] == "Chord"
    assert revs[0]["key"] == "D"

    assert revs[1]["rev_type"] == "song_version"
    assert revs[1]["label"] == "from foo"

    # now delete everything
    response = client.http.delete(
        f"/songs/{song_id}/versions/{song_version_id}/sheets/{song_sheet_id}"
    )
    assert response.status_code == 204

    response = client.http.delete(f"/songs/{song_id}/versions/{song_version_id}")
    assert response.status_code == 204

    response = client.http.delete(f"/songs/{song_id}")
    assert response.status_code == 204

    response = client.http.get(f"/songs/{song_id}/revisions")
    assert response.status_code == 200
    revs = response.json_body["song_revisions"]

    assert len(revs) == 5
    assert revs[0]["rev_type"] == "song_sheet"
    assert revs[0]["type"] == "Lead"
    assert revs[0]["key"] == "C"

    assert revs[1]["rev_type"] == "song_version"
    assert revs[1]["label"] == "From Foo"

    assert revs[-1]["rev_type"] == "song"
    assert revs[-1]["id"] == song_id
