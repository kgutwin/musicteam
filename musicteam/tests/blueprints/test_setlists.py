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


def test_setlists_get_music_packet(client, mock_storage, pdf_snapshot):
    mock_storage.data["xyzxyzxyz"] = b"blah blah blah"

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
            "object_id": "xyzxyzxyz",
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

    # get packet
    response = client.http.get(
        f"/setlists/{setlist_id}/packet/pdf", headers={"Accept": "application/pdf"}
    )
    assert response.status_code == 200, response.body
    assert response.body == pdf_snapshot(name="packet")

    # we should have a packet stored now
    response = client.http.get(f"/setlists/{setlist_id}")
    assert response.status_code == 200, response.body
    assert response.json_body["music_packet_object_id"] is not None
    music_packet_object_id = response.json_body["music_packet_object_id"]

    assert len(mock_storage.data[music_packet_object_id]) == 432482

    # get packet a second time
    response = client.http.get(
        f"/setlists/{setlist_id}/packet/pdf", headers={"Accept": "application/pdf"}
    )
    assert response.status_code == 200, response.body
    assert response.body == pdf_snapshot(name="packet")

    # if we change the setlist, the packet will change
    response = client.http.put(f"/setlists/{setlist_id}", json={"leader_name": "jane"})
    assert response.status_code == 204, response.body

    response = client.http.get(
        f"/setlists/{setlist_id}/packet/pdf", headers={"Accept": "application/pdf"}
    )
    assert response.status_code == 200, response.body

    response = client.http.get(f"/setlists/{setlist_id}")
    assert response.status_code == 200, response.body
    assert response.json_body["music_packet_object_id"] is not None
    assert response.json_body["music_packet_object_id"] != music_packet_object_id
