from typing import Any

from chalice.app import Chalice
from chalicelib import db
from chalicelib import middleware
from chalicelib.blueprints import auth
from chalicelib.types import TestRow

app = Chalice(app_name="musicteam")

middleware.register(app)
app.register_blueprint(auth.bp)


@app.route("/")
def index() -> dict[str, Any]:
    count = -1
    msg = "world"
    try:
        with db.connect() as conn:
            curs = conn.execute("SELECT count(*) AS count FROM users;", output=TestRow)
            result = curs.fetchone()
            if result:
                count = result.count
    except BaseException as ex:
        msg = str(ex)
    return {"hello": msg, "count": count}


@app.route("/names/{name}", methods=["POST"])
def names(name: str, request_body: TestRow) -> TestRow:
    print(request_body)
    return request_body


@app.route("/admin/db-upgrade/{ver}", methods=["POST"])
def db_upgrade(ver: str) -> dict[str, Any]:
    db.upgrade_to(ver)
    return {"status": "ok"}
