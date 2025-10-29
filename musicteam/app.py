from typing import Any

from chalice.app import Chalice
from chalicelib import middleware
from chalicelib.blueprints import auth
from chalicelib.blueprints import comments
from chalicelib.blueprints import objects
from chalicelib.blueprints import setlists
from chalicelib.blueprints import songs
from chalicelib.blueprints import users

app = Chalice(app_name="musicteam")

middleware.register(app)
app.register_blueprint(auth.bp)
app.register_blueprint(comments.bp)
app.register_blueprint(objects.bp)
app.register_blueprint(setlists.bp)
app.register_blueprint(songs.bp)
app.register_blueprint(users.bp)


@app.route("/")
def index() -> dict[str, Any]:
    return {"status": "tbd"}
