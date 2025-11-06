import inspect
import time
from http.cookies import SimpleCookie
from typing import Any
from typing import Callable
from typing import cast
from typing import Mapping
from typing import Self
from typing import TypeVar

import jwt.exceptions
from chalice.app import Chalice
from chalice.app import Request
from chalice.app import Response
from chalicelib import db
from chalicelib.types import BadRequest
from chalicelib.types import User
from chalicelib.types import UserRole
from pydantic import ValidationError

T = TypeVar("T")


class CookieJar:
    """Basic cookie management.

    >>> c = CookieJar('foo=bar; baz="quux"')
    >>> c['foo']
    'bar'
    >>> c['baz']
    'quux'
    >>> c['baz'] = 'something "new"'
    >>> c['baz']
    'something "new"'
    >>> c.should_set
    True
    >>> c.set_header  # doctest: +NORMALIZE_WHITESPACE
    {'Set-Cookie': ['baz="something \\\\"new\\\\""; HttpOnly; SameSite=Strict',
                    'foo=bar']}

    """

    def __init__(self, cookie_str: str) -> None:
        self._cookie = SimpleCookie(cookie_str)
        self._dirty = False

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> Self:
        if "Cookie" in headers:
            return cls(headers["Cookie"])
        return cls("")

    def __getitem__(self, key: str) -> str:
        return self._cookie[key].value

    def __setitem__(self, key: str, value: str | None) -> None:
        if not value:
            self._cookie[key] = ""
            self._cookie[key]["max-age"] = 0
        else:
            self._cookie[key] = value
        self._cookie[key]["httponly"] = True
        self._cookie[key]["path"] = "/"
        # self._cookie[key]["secure"] = True
        # self._cookie[key]["samesite"] = "Strict"
        self._dirty = True

    def __repr__(self) -> str:
        return repr(self._cookie)

    @property
    def should_set(self) -> bool:
        return self._dirty

    @should_set.setter
    def should_set(self, val: bool) -> None:
        self._dirty = True

    @property
    def set_header(self) -> dict[str, list[str]]:
        output = self._cookie.output(header="")
        return {"Set-Cookie": [i.strip() for i in output.split("\r\n")]}


def register(app: Chalice) -> None:
    @app.middleware("all")
    def wake_db(event: T, get_response: Callable[[T], Any]) -> Any:
        while not db.ping():
            time.sleep(1)
        return get_response(event)

    @app.middleware("http")
    def handle_modeled_body(
        event: Request, get_response: Callable[[Request], Response]
    ) -> Response:
        try:
            resource_path = event.context["resourcePath"]
            http_method = event.context["httpMethod"]
            route = app.routes[resource_path][http_method]
        except KeyError:
            return get_response(event)

        sig = inspect.signature(route.view_function)
        try:
            if "request_body" in sig.parameters:
                if "request_body" not in route.view_args:
                    route.view_args.append("request_body")
                klass = sig.parameters["request_body"].annotation
                if not event._event_dict.get("pathParameters"):
                    event._event_dict["pathParameters"] = {}
                if klass is bytes:
                    event._event_dict["pathParameters"]["request_body"] = event.raw_body
                elif hasattr(klass, "model_validate"):
                    request_body = klass.model_validate(event.json_body)
                    event._event_dict["pathParameters"]["request_body"] = request_body
                else:
                    raise TypeError(klass)

            if "query_params" in sig.parameters:
                if "query_params" not in route.view_args:
                    route.view_args.append("query_params")
                klass = sig.parameters["query_params"].annotation
                if not event._event_dict.get("pathParameters"):
                    event._event_dict["pathParameters"] = {}
                if hasattr(klass, "model_validate"):
                    query_params = klass.model_validate(event.query_params or {})
                    event._event_dict["pathParameters"]["query_params"] = query_params
                else:
                    raise TypeError(klass)

            response = get_response(event)

        except ValidationError as ex:
            response = BadRequest(str(ex))

        if hasattr(response.body, "model_dump"):
            response.body = response.body.model_dump(mode="json")

        return response

    @app.middleware("http")
    def handle_cookies(
        event: Request, get_response: Callable[[Request], Response]
    ) -> Response:
        # parse cookies from event
        cookie_jar = CookieJar.from_headers(event.headers)
        event.context["cookies"] = cookie_jar

        response = get_response(event)
        if cookie_jar.should_set:
            response.headers.update(cookie_jar.set_header)

        return response

    @app.middleware("http")
    def add_user_session(
        event: Request, get_response: Callable[[Request], Response]
    ) -> Response:
        token = None
        try:
            token = event.context["cookies"]["session"]
        except KeyError:
            try:
                token = event.context["cookies"]["auth.token"]
            except KeyError:
                pass

        if token is not None:
            try:
                user = User.from_token(token)
                event.context["user"] = user
            except jwt.exceptions.InvalidTokenError:
                pass

        return get_response(event)


def session_user(request: Request) -> User:
    if "user" not in request.context:
        return User.unauthenticated()
    return cast(User, request.context["user"])


def session_role(request: Request, role: UserRole) -> bool:
    if "user" not in request.context:
        return False
    return cast(User, request.context["user"]).has_role(role)
