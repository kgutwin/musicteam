from typing import Any

from chalice.app import Chalice
from chalicelib import _deployed_at
from chalicelib import _version
from chalicelib import middleware
from chalicelib import semantic
from chalicelib.blueprints import auth
from chalicelib.blueprints import comments
from chalicelib.blueprints import history
from chalicelib.blueprints import info
from chalicelib.blueprints import objects
from chalicelib.blueprints import setlists
from chalicelib.blueprints import songs
from chalicelib.blueprints import users
from chalicelib.types import IndexResponse
from chalicelib.types import NoContent

app = Chalice(app_name="musicteam")
app.api.binary_types.append("application/pdf")
# needed for some reason to get PDFs working in Safari?
app.api.binary_types.append("text/html")

middleware.register(app)
app.register_blueprint(auth.bp)
app.register_blueprint(comments.bp)
app.register_blueprint(objects.bp)
app.register_blueprint(setlists.bp)
app.register_blueprint(songs.bp)
app.register_blueprint(users.bp)
app.register_blueprint(info.bp)
app.register_blueprint(history.bp)


@app.route("/")
@middleware.no_ping_db
def index() -> IndexResponse:
    return IndexResponse(status="ok", version=_version()[:7], deployedAt=_deployed_at())


@app.route("/ping")
def ping() -> NoContent:
    """Wake the backend database"""
    return NoContent()


@app.lambda_function()
def semantic_similarity_encoder(event: dict[str, Any], context: Any) -> None:
    if "song_version_id" in event:
        semantic.compute_lyrics_vector(event["song_version_id"])
    else:
        for song_version_id in semantic.get_missing_lyrics_vectors():
            semantic.compute_lyrics_vector(song_version_id)
            if context.get_remaining_time_in_millis() < 2000:
                print("Not enough time left...")
                break


if __name__ == "__main__":
    import sys
    import json

    if sys.argv[1] == "invoke-lambda":
        func = locals()[sys.argv[2]]
        event = json.loads(sys.argv[3])

        class MockLambdaContext:
            def get_remaining_time_in_millis(self) -> int:
                return 5000

        result = func(event, MockLambdaContext())

        print(json.dumps(result))
