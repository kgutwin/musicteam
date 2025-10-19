import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Literal
from typing import Self

import jwt
from chalice.app import HeadersType
from chalice.app import Response
from pydantic import BaseModel

SITE_SECRET = os.environ["SITE_SECRET"]


# API Models


class ServerError(BaseModel):
    error: str
    detail: str


class TestRow(BaseModel):
    count: int


class LoginResponse(BaseModel):
    token: str


class User(BaseModel):
    id: str
    name: str
    provider_id: str
    email: str
    picture: str
    role: Literal["admin", "manager", "leader", "viewer", "pending", "inactive"]
    api_key: str | None

    @classmethod
    def from_token(cls, token: str) -> Self:
        return cls.model_validate(jwt.decode(token, SITE_SECRET, algorithms="HS256"))

    def to_token(self) -> str:
        return jwt.encode(
            {
                "nbf": datetime.now(tz=timezone.utc),
                "exp": datetime.now(tz=timezone.utc) + timedelta(days=14),
            }
            | self.model_dump(),
            SITE_SECRET,
            algorithm="HS256",
        )


# Chalice response types
class KnownResponse(Response):
    _code = 200
    _response_model: type[BaseModel] | None = None

    def __init__(self, body: Any = "", headers: HeadersType | None = None):
        super().__init__(body, headers, self._code)


class NoContent(KnownResponse):
    """No Content. The request was successful but there is nothing to return."""

    _code = 204


class Found(KnownResponse):
    """Found. The URI of the requested resource has been changed temporarily."""

    _code = 302

    def __init__(self, location: str):
        super().__init__(headers={"Location": location})


class Forbidden(KnownResponse):
    """Forbidden. Based on your user permissions, you may not perform this operation."""

    _code = 403


class Error(KnownResponse):
    """Error. Something went wrong on the server side."""

    _code = 500
    _response_model = ServerError
