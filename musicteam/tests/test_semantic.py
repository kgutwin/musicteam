import pytest
from pydantic import BaseModel


@pytest.fixture
def song(client):
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
        f"/songs/{song_id}/versions",
        json={"label": "from foo", "lyrics": "one two three four five"},
    )
    assert response.status_code == 200
    song_version_id = response.json_body["id"]

    return {"song_id": song_id, "version_id": song_version_id}


class EmbeddingResult(BaseModel):
    lyrics_embedding: str


def test_compute_lyrics_vector(client, db, song, snapshot):
    song_version_id = song["version_id"]

    result = client.lambda_.invoke(
        "semantic_similarity_encoder", {"song_version_id": song_version_id}
    )

    # check that the vector is in the database
    with db.connect() as conn:
        result = conn.execute(
            "SELECT lyrics_embedding FROM song_versions", output=EmbeddingResult
        ).fetchone()
        assert result.lyrics_embedding == snapshot


def test_compute_missing_lyrics_vectors(client, db, song, snapshot):
    # basically the same as the above except not specifying the song version id
    result = client.lambda_.invoke("semantic_similarity_encoder", {})

    # check that the vector is in the database
    with db.connect() as conn:
        result = conn.execute(
            "SELECT lyrics_embedding FROM song_versions", output=EmbeddingResult
        ).fetchone()
        assert result.lyrics_embedding == snapshot
