import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import Iterator
from typing import TYPE_CHECKING

import boto3
from chalicelib import db
from pydantic import BaseModel

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
else:
    SentenceTransformer = Any

logger = logging.getLogger(__name__)
client = boto3.client("lambda")

MODEL_NAME = "LoveJesus/biblical-topical-search-chirho"
MODEL_FILE_NAME = MODEL_NAME.replace("/", "--")
MODEL: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer

        # look in the lambda layer location
        lambda_loc = (
            Path("/opt/python/lib")
            / f"python{sys.version_info[0]}.{sys.version_info[1]}"
            / "site-packages"
            / MODEL_FILE_NAME
        )
        if lambda_loc.exists():
            MODEL = SentenceTransformer(str(lambda_loc), local_files_only=True)
        else:
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


def invoke(event: dict[str, str]) -> None:
    """Invoke the Lambda function, whether deployed or local testing."""

    return  # out of curiosity, does this help?

    lambda_arn = os.environ.get("LAMBDA_ARN_SEMANTIC_SIMILARITY_ENCODER")
    if lambda_arn:
        client.invoke(
            FunctionName=lambda_arn,
            InvokationType="Event",
            Payload=json.dumps(event).encode(),
        )

    else:
        subprocess.Popen(
            [
                "python",
                "-m",
                "app",
                "invoke-lambda",
                "semantic_similarity_encoder",
                json.dumps(event),
            ]
        )


def reindex_song_lyrics(song_version_id: str) -> None:
    return invoke({"compute_lyrics_vector": song_version_id})


if __name__ == "__main__":
    if sys.argv[1] == "fetch":
        print("Loading", MODEL_NAME, "...")
        model = _load_model()
        print("Saving to", MODEL_FILE_NAME, "...")
        model.save(f"vendor/{MODEL_FILE_NAME}")
