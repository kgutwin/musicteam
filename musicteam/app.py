from typing import Any

from chalice.app import Chalice
from chalicelib import db
from chalicelib import middleware
from chalicelib.blueprints import auth
from chalicelib.blueprints import users

app = Chalice(app_name="musicteam")

middleware.register(app)
app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)


@app.route("/")
def index() -> dict[str, Any]:
    return {"status": "tbd"}


@app.route("/admin/db-upgrade/{ver}", methods=["POST"])
def db_upgrade(ver: str) -> dict[str, Any]:
    db.upgrade_to(ver)
    return {"status": "ok"}
