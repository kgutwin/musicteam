import time
import inspect
from functools import wraps
from typing import Any, Callable, TypeVar

from chalice.app import Chalice, Request
from chalicelib import db, middleware
from chalicelib.types import TestRow

app = Chalice(app_name="musicteam")

middleware.register(app)


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


@app.route("/auth/login", methods=["POST"])
def auth_login() -> dict[str, Any]:
    if app.current_request is not None:
        print(app.current_request.raw_body)
        print(app.current_request.context["cookies"])
        app.current_request.context["cookies"]["session"] = "a1b2c3d4"
    return {
        "status": "ok",
        "token": "aaaaaaaa",
    }


@app.route("/auth/logout", methods=["POST"])
def auth_logout() -> dict[str, Any]:
    return {"status": "ok"}  # probably 204 instead


@app.route("/auth/session", methods=["GET"])
def auth_session() -> dict[str, Any]:
    return {
        "id": "11111111",
        "name": "hello user",
        "email": "user@example.com",
        "role": "admin",
    }


@app.route("/admin/db-upgrade/{ver}", methods=["POST"])
def db_upgrade(ver: str) -> dict[str, Any]:
    db.upgrade_to(ver)
    return {"status": "ok"}
