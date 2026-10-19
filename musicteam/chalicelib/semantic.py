import json
import logging
import os
import socket
import socketserver
import subprocess
import sys
import time
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
MODEL_DIR_NAME = Path("/var/cache") / MODEL_NAME.replace("/", "--")
MODEL: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer

        # look in the lambda cache location
        if MODEL_DIR_NAME.exists():
            MODEL = SentenceTransformer(str(MODEL_DIR_NAME), local_files_only=True)
        else:
            MODEL = SentenceTransformer(MODEL_NAME)

    return MODEL


class SongVersionLyrics(BaseModel):
    lyrics: str | None


def compute_lyrics_vector(song_version_id: str) -> None:
    print(f"======== computing vector for {song_version_id=}")
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
            "UPDATE song_versions SET lyrics_embedding = cast(:vector AS VECTOR)"
            "WHERE id = :version_id",
            {"version_id": song_version_id, "vector": str(embeddings.tolist())},
        )
    print(f"======== completed vector for {song_version_id=}")


class SongVersionId(BaseModel):
    id: str


def get_missing_lyrics_vectors() -> Iterator[str]:
    while True:
        with db.connect() as conn:
            result = conn.execute(
                "SELECT id FROM song_versions "
                "WHERE lyrics IS NOT NULL and lyrics_embedding IS NULL "
                "LIMIT 1",
                output=SongVersionId,
            ).fetchone()

        if result is None:
            break
        else:
            yield result.id


def handler(event: dict[str, str], context: Any) -> None:
    if "compute_lyrics_vector" in event:
        compute_lyrics_vector(event["compute_lyrics_vector"])
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


class InvokeHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        event = json.load(self.rfile)
        handler(event, None)


class InvokeServer(socketserver.TCPServer):
    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, InvokeHandler)
        self.watchdog = time.monotonic()

    def service_actions(self) -> None:
        if time.monotonic() > self.watchdog + 10.0:
            print("-------- invoke server shutting down")
            sys.exit(0)

    def verify_request(self, *args: Any) -> bool:
        self.watchdog = time.monotonic()
        return True


if __name__ == "__main__":
    if sys.argv[1] == "fetch":
        print("Loading", MODEL_NAME, "...")
        model = _load_model()
        print("Saving to", MODEL_DIR_NAME, "...")
        model.save(str(MODEL_DIR_NAME))
        # for some reason, the safetensors file is being saved mod 600
        # but it needs to be mod 644
        (MODEL_DIR_NAME / "model.safetensors").chmod(0o644)

    elif sys.argv[1] == "invoke":
        HOST, PORT = "localhost", 9999

        try:
            with InvokeServer((HOST, PORT)) as server:
                # first handle the proximal event
                event = json.loads(sys.argv[2])
                handler(event, None)

                # start the server to handle future events
                print("-------- invoke server startup")
                server.serve_forever()
            sys.exit(0)

        except OSError as ex:
            if "Address already in use" not in str(ex):
                raise

            # send the event to the running server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, PORT))
                sock.sendall(sys.argv[2].encode())
                sock.sendall(b"\n")
