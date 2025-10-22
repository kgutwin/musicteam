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
from pydantic import Field

SITE_SECRET = os.environ["SITE_SECRET"]


class _ReplacementModel(BaseModel):
    @property
    def replacement_sql(self) -> str:
        return ", ".join(f"{field} = :{field}" for field in self.model_fields_set)

    @property
    def replacement_params(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.model_fields_set}


# API Models


class ServerError(BaseModel):
    Code: str
    Message: str


class LoginResponse(BaseModel):
    token: str


UserRole = Literal["admin", "manager", "leader", "viewer", "pending", "inactive"]


class User(BaseModel):
    id: str
    name: str
    provider_id: str
    email: str
    picture: str
    role: UserRole
    api_key: str | None = None

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

    def has_role(self, role: UserRole) -> bool:
        """True if this user's role is equal or higher to the provided role."""
        role_order: list[UserRole] = [
            "admin",
            "manager",
            "leader",
            "viewer",
            "pending",
            "inactive",
        ]
        return role_order.index(self.role) <= role_order.index(role)


class UserList(BaseModel):
    users: list[User]


class NewSong(BaseModel):
    title: str
    credits: str
    ccli_num: int | None = Field(title="CCLI Number")
    tags: list[str]


class UpdateSong(_ReplacementModel):
    title: str | None = None
    credits: str | None = None
    ccli_num: int | None = Field(None, title="CCLI Number")
    tags: list[str] | None = None


class Song(NewSong):
    id: str
    created_on: datetime
    creator_id: str


class SongList(BaseModel):
    songs: list[Song]


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


class NotFound(KnownResponse):
    """Not Found. The requested resource does not exist."""

    _code = 404


class Error(KnownResponse):
    """Error. Something went wrong on the server side."""

    _code = 500
    _response_model = ServerError
