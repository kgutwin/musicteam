from typing import Any
from typing import Iterator
from typing import TYPE_CHECKING

from pydantic import BaseModel

from . import db

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
else:
    SentenceTransformer = Any


MODEL_NAME = "LoveJesus/biblical-topical-search-chirho"
MODEL: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer

        MODEL = SentenceTransformer(MODEL_NAME)

    return MODEL


class SongVersionLyrics(BaseModel):
    lyrics: str | None


def compute_lyrics_vector(song_version_id: str) -> None:
    with db.connect() as conn:
        result = conn.execute(
            "SELECT lyrics FROM song_versions WHERE id = :version_id",
            {"version_id": song_version_id},
            output=SongVersionLyrics,
        ).fetchone()

        if result is None or result.lyrics is None:
            return

    model = _load_model()

    embeddings = model.encode(result.lyrics)

    with db.connect() as conn:
        conn.execute(
            "UPDATE song_versions SET lyrics_embedding = :vector "
            "WHERE id = :version_id",
            {"version_id": song_version_id, "vector": str(embeddings.tolist())},
        )


class SongVersionId(BaseModel):
    id: str


def get_missing_lyrics_vectors() -> Iterator[str]:
    with db.connect() as conn:
        while True:
            result = conn.execute(
                "SELECT id FROM song_versions WHERE lyrics_embedding IS NULL LIMIT 1",
                output=SongVersionId,
            ).fetchone()

            if result is None:
                break
            else:
                yield result.id
