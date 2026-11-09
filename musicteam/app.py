from chalice.app import Chalice
from chalicelib import _deployed_at, _version, middleware
from chalicelib.blueprints import (
    auth,
    comments,
    history,
    info,
    objects,
    setlists,
    songs,
    users,
)
from chalicelib.types import IndexResponse, NoContent

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
