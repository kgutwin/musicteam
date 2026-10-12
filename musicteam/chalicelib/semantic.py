import logging
from typing import Any
from typing import Iterator
from typing import TYPE_CHECKING

from pydantic import BaseModel

from . import db

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
else:
    SentenceTransformer = Any

logger = logging.getLogger(__name__)


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
            logger.warning(f"could not find lyrics for {song_version_id=}")
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
    while True:
        with db.connect() as conn:
            result = conn.execute(
                "SELECT id FROM song_versions WHERE lyrics_embedding IS NULL LIMIT 1",
                output=SongVersionId,
            ).fetchone()

        if result is None:
            break
        else:
            yield result.id


# notes:
# - I don't think chalice local will help us run our pure lambda function.
#   Therefore, I think instead we just need to have a function which:
#   - if the right env var is set, invokes boto3 to call the real Lambda
#   - otherwise, does a subprocess/fork so that we call self in such a way
#     that the function runs with the right args but in the background
#
# - we still need to figure out how to pre-download the model and then make
#   sure that when called from the function, it works fine
#
# - looks like Torch can't work inside an Alpine container, so our Dockerfile
#   will need to switch to base python:3.13
