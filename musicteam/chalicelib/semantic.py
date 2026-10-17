import json
import logging
import os
import subprocess
import sys
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


def handler(event: dict[str, str], context: Any) -> None:
    if "song_version_id" in event:
        compute_lyrics_vector(event["song_version_id"])
    else:
        for song_version_id in get_missing_lyrics_vectors():
            compute_lyrics_vector(song_version_id)
            if context and context.get_remaining_time_in_millis() < 2000:
                print("not enough time left...")
                break


def invoke(event: dict[str, str]) -> None:
    """Invoke the Lambda function, whether deployed or local testing."""

    lambda_arn = os.environ.get("LAMBDA_ARN_SEMANTIC_SIMILARITY_ENCODER")
    if lambda_arn:
        client.invoke(
            FunctionName=lambda_arn,
            InvocationType="Event",
            Payload=json.dumps(event).encode(),
        )

    elif os.environ.get("AWS_CHALICE_CLI_MODE"):
        subprocess.Popen(
            [
                "python",
                "-m",
                "chalicelib.semantic",
                "invoke",
                json.dumps(event),
            ]
        )

    else:
        logger.warning("Must define LAMBDA_ARN_SEMANTIC_SIMILARITY_ENCODER")


def reindex_song_lyrics(song_version_id: str) -> None:
    return invoke({"compute_lyrics_vector": song_version_id})


if __name__ == "__main__":
    if sys.argv[1] == "fetch":
        print("Loading", MODEL_NAME, "...")
        model = _load_model()

    elif sys.argv[1] == "invoke":
        event = json.loads(sys.argv[2])
        handler(event, None)
