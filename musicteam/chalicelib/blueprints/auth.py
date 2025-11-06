import google.auth.transport.requests
import google.oauth2.id_token
import jwt.exceptions
from chalice.app import Blueprint
from chalice.app import Request
from chalicelib import db
from chalicelib.config import OAUTH_CLIENT_ID
from chalicelib.config import OAUTH_CLIENT_SECRET
from chalicelib.types import Forbidden
from chalicelib.types import Found
from chalicelib.types import LoginResponse
from chalicelib.types import NoContent
from chalicelib.types import User
from requests_oauthlib import OAuth2Session

bp = Blueprint(__name__)

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def url_for(request: Request, suffix: str) -> str:
    proto = request.headers.get(
        "x-dev-proto", request.headers.get("x-forwarded-proto", "https")
    )
    host = request.headers.get(
        "x-dev-host",
        request.headers.get(
            "x-original-host", request.headers.get("host", "localhost")
        ),
    )
    return f"{proto}://{host}/api{suffix}"


@bp.route("/auth/google", methods=["GET"])
def auth_google() -> Found:
    redirect_uri = url_for(bp.current_request, "/auth/callback")

    if OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET:
        oauth_session = OAuth2Session(
            OAUTH_CLIENT_ID, scope=SCOPE, redirect_uri=redirect_uri
        )
        authorization_url, state = oauth_session.authorization_url(
            AUTHORIZATION_BASE_URL
        )
        bp.current_request.context["cookies"]["state"] = state

    else:
        # bypassing OAuth since client and secret are not defined
        authorization_url = redirect_uri

    return Found(authorization_url)


@bp.route("/auth/callback", methods=["GET"])
def auth_callback() -> Forbidden | Found:
    if OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET:
        assert bp.current_request.query_params is not None
        state = bp.current_request.query_params.get("state")

        if state != bp.current_request.context["cookies"]["state"]:
            return Forbidden("invalid request state")

        redirect_uri = url_for(bp.current_request, "/auth/callback")
        oauth_session = OAuth2Session(
            OAUTH_CLIENT_ID, state=state, redirect_uri=redirect_uri
        )
        token = oauth_session.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH_CLIENT_SECRET,
            code=bp.current_request.query_params["code"],
        )

        payload = google.oauth2.id_token.verify_oauth2_token(  # type: ignore[no-untyped-call]
            token["id_token"],
            google.auth.transport.requests.Request(),  # type: ignore[no-untyped-call]
            OAUTH_CLIENT_ID,
        )

    else:
        # bypassing OAuth since client and secret are not defined
        payload = {
            "name": "Local User",
            "sub": "1111222233334444",
            "email": "user@example.com",
            "picture": None,
        }

    with db.connect() as conn:
        curs = conn.execute(
            (
                "INSERT INTO users (name, provider_id, email, picture, role) "
                "VALUES (:name, :provider_id, :email, :picture, :role) "
                "ON CONFLICT (provider_id) DO UPDATE"
                "  SET name = EXCLUDED.name, email = EXCLUDED.email,"
                "  picture = EXCLUDED.picture "
                "RETURNING id, name, provider_id, email, picture, role"
            ),
            {
                "name": payload["name"],
                "provider_id": payload["sub"],
                "email": payload["email"],
                "picture": payload["picture"],
                "role": "admin",
            },
            output=User,
        )
        user = curs.fetchone()
        assert user is not None

    bp.current_request.context["cookies"]["session"] = user.to_token()
    bp.current_request.context["cookies"]["state"] = None

    return Found("/login?complete=1")


@bp.route("/auth/login", methods=["POST"])
def auth_login() -> LoginResponse | Forbidden:
    # check the session cookie and return any necessary response
    try:
        token = bp.current_request.context["cookies"]["session"]
        return LoginResponse(token=token)
    except KeyError:
        return Forbidden()


@bp.route("/auth/logout", methods=["POST"])
def auth_logout() -> NoContent:
    bp.current_request.context["cookies"]["session"] = None
    return NoContent()


@bp.route("/auth/session", methods=["GET"])
def auth_session() -> User | NoContent:
    # check the session cookie and return any necessary response
    try:
        token = bp.current_request.context["cookies"]["session"]
        return User.from_token(token)
    except (KeyError, jwt.exceptions.InvalidTokenError):
        return NoContent()


# TODO: consider de-duplicating the auth.token (nuxt auth stuff)
# cookie from our own session cookie, possibly using nuxt auth session
# refresh
