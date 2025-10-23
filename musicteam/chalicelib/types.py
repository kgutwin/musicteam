import os
from datetime import date
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
    def any_replacements(self) -> bool:
        return bool(self.model_fields_set)

    @property
    def replacement_sql(self) -> str:
        return ", ".join(f"{field} = :{field}" for field in self.model_fields_set)

    @property
    def replacement_params(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.model_fields_set}


class _CoreModel(BaseModel):
    id: str
    created_on: datetime
    creator_id: str


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

    @classmethod
    def unauthenticated(cls) -> Self:
        return cls(
            id="u:00000000-0000-0000-0000-000000000000",
            name="Unauthenticated",
            provider_id="",
            email="",
            picture="",
            role="pending",
        )


class UserList(BaseModel):
    users: list[User]


class NewSong(BaseModel):
    title: str
    authors: list[str]
    ccli_num: int | None = Field(title="CCLI Number")
    tags: list[str] = []


class UpdateSong(_ReplacementModel):
    title: str | None = None
    authors: list[str] | None = None
    ccli_num: int | None = Field(None, title="CCLI Number")
    tags: list[str] | None = None


class Song(_CoreModel, NewSong):
    pass


class SongList(BaseModel):
    songs: list[Song]


class NewSongVersion(BaseModel):
    label: str
    verse_order: str | None = None
    lyrics: str | None = None
    tags: list[str] = []


class UpdateSongVersion(_ReplacementModel):
    label: str | None = None
    verse_order: str | None = None
    lyrics: str | None = None
    tags: list[str] | None = None


class SongVersion(_CoreModel, NewSongVersion):
    song_id: str


class SongVersionList(BaseModel):
    song_versions: list[SongVersion]


class NewSongSheet(BaseModel):
    type: Literal["pdf", "text", "musicxml"]
    key: str
    tags: list[str] = []
    object_id: str


class UpdateSongSheet(_ReplacementModel):
    key: str | None = None
    tags: list[str] | None = None
    object_id: str | None = None


class SongSheet(_CoreModel, NewSongSheet):
    song_version_id: str


class SongSheetList(BaseModel):
    song_sheets: list[SongSheet]


class NewSetlist(BaseModel):
    leader_name: str
    service_date: date | None = None
    tags: list[str] = []


class UpdateSetlist(_ReplacementModel):
    leader_name: str | None = None
    service_date: date | None = None
    tags: list[str] | None = None
    music_packet_object_id: str | None = None
    lyric_packet_object_id: str | None = None


class Setlist(_CoreModel, NewSetlist):
    pass


class SetlistList(BaseModel):
    setlists: list[Setlist]


class NewSetlistPosition(BaseModel):
    index: int
    label: str
    is_music: bool
    presenter: str | None = None
    status: Literal["open", "in-progress", "final"] | None = None


class UpdateSetlistPosition(_ReplacementModel):
    index: int | None = None
    label: str | None = None
    is_music: bool | None = None
    presenter: str | None = None
    status: Literal["open", "in-progress", "final"] | None = None


class SetlistPosition(NewSetlistPosition):
    id: str
    setlist_id: str


class SetlistPositionList(BaseModel):
    positions: list[SetlistPosition]


SetlistSheetType = Literal[
    "1:primary",
    "2:secondary",
    "3:extra",
    "4:candidate-high",
    "5:candidate",
    "6:candidate-low",
]


class NewSetlistSheet(BaseModel):
    type: SetlistSheetType
    song_sheet_id: str
    setlist_position_id: str | None = None


class UpdateSetlistSheet(_ReplacementModel):
    type: SetlistSheetType | None = None
    setlist_position_id: str | None = None


class SetlistSheet(NewSetlistSheet):
    id: str
    setlist_id: str
    title: str
    key: str


class SetlistSheetList(BaseModel):
    sheets: list[SetlistSheet]


class NewSetlistTemplate(BaseModel):
    title: str
    tags: list[str] = []


class UpdateSetlistTemplate(_ReplacementModel):
    title: str | None = None
    tags: list[str] | None = None


class SetlistTemplate(_CoreModel, NewSetlistTemplate):
    pass


class SetlistTemplateList(BaseModel):
    templates: list[SetlistTemplate]


class NewSetlistTemplatePosition(BaseModel):
    index: int
    label: str
    is_music: bool
    presenter: str | None = None


class UpdateSetlistTemplatePosition(_ReplacementModel):
    index: int | None = None
    label: str | None = None
    is_music: bool | None = None
    presenter: str | None = None


class SetlistTemplatePosition(NewSetlistTemplatePosition):
    id: str
    template_id: str


class SetlistTemplatePositionList(BaseModel):
    positions: list[SetlistTemplatePosition]


class NewComment(BaseModel):
    comment: str


class UpdateComment(_ReplacementModel):
    comment: str | None = None


class Comment(_CoreModel, NewComment):
    resource_id: str


class CommentList(BaseModel):
    comments: list[Comment]


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
