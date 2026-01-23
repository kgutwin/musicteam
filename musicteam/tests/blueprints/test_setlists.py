def test_setlists_add_song(client):
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
        f"/songs/{song_id}/versions", json={"label": "from pytest"}
    )
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
    song_sheet_id = response.json_body["id"]

    # create a set list
    response = client.http.post(
        "/setlists",
        json={"leader_name": "joe", "service_date": "2026-01-25", "tags": ["pytest"]},
    )
    setlist_id = response.json_body["id"]

    response = client.http.post(
        f"/setlists/{setlist_id}/pos",
        json={"index": 0, "label": "position", "is_music": True},
    )
    setlist_position_id = response.json_body["id"]

    # add song to position
    response = client.http.post(
        f"/setlists/{setlist_id}/sheets",
        json={
            "type": "1:primary",
            "song_sheet_id": song_sheet_id,
            "setlist_position_id": setlist_position_id,
        },
    )
    assert response.status_code == 200, response.body

    # can't delete the song
    response = client.http.delete(f"/songs/{song_id}")
    assert response.status_code == 400

    # but if we delete the setlist
    response = client.http.delete(f"/setlists/{setlist_id}")
    assert response.status_code == 204

    # then we can delete the song
    response = client.http.delete(f"/songs/{song_id}")
    assert response.status_code == 204
