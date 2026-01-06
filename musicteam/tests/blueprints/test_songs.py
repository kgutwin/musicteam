from chalicelib.types import SongRevision


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


def test_songs_update(client, db):
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

    with db.connect() as conn:
        curs = conn.execute("SELECT * FROM rev_songs", output=SongRevision)
        revs = curs.fetchall()
        assert len(revs) == 1
        assert revs[0].title == "test song"
        assert revs[0].id == song_id
        assert revs[0].rev_changed_by == "u:41c95da1-7eaf-4d0f-8669-6df165204d6c"
