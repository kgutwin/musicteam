import contextlib
import os.path
import re
from typing import Any
from typing import cast
from typing import Generic
from typing import Iterator
from typing import Mapping
from typing import overload
from typing import TypeVar

import aurora_data_api
from pydantic import BaseModel

PSYCOPG_PARAM: re.Pattern[str] | None
try:
    from py_pglite import PGliteManager, PGliteConfig  # type: ignore[import-untyped]
    import psycopg

    import py_pglite.extensions  # type: ignore[import-untyped]

    py_pglite.extensions.SUPPORTED_EXTENSIONS["uuid_ossp"] = {
        "module": "@electric-sql/pglite/contrib/uuid_ossp",
        "name": "uuid_ossp",
    }

    PGLITE_AVAILABLE = True
    PGLITE_MANAGER: PGliteManager | None = None

    PSYCOPG_PARAM = re.compile(r"(?<=[^:]):(\w+)")

except ImportError:
    PGLITE_AVAILABLE = False
    PSYCOPG_PARAM = None


T = TypeVar("T", bound=BaseModel)


class Cursor(Generic[T]):
    def __init__(self, curs: aurora_data_api.AuroraDataAPICursor, model: type[T]):
        self.curs = curs
        self.model = model

    def __iter__(self) -> Iterator[T]:
        assert self.curs.description is not None
        for row in self.curs:
            d = {self.curs.description[i].name: v for i, v in enumerate(row)}
            yield self.model.model_validate(d)

    def fetchone(self) -> T | None:
        try:
            return next(iter(self))
        except StopIteration:
            return None

    def fetchall(self) -> list[T]:
        return list(self)


class Interface:
    def __init__(self, conn: aurora_data_api.AuroraDataAPIClient):
        self.conn = conn

    @overload
    def execute(
        self, sql: str, parameters: Mapping[str, Any] | BaseModel | None = None
    ) -> None: ...

    @overload
    def execute(
        self,
        sql: str,
        parameters: Mapping[str, Any] | BaseModel | None = None,
        *,
        output: type[T],
    ) -> Cursor[T]: ...

    def execute(
        self,
        sql: str,
        parameters: Mapping[str, Any] | BaseModel | None = None,
        *,
        output: type[T] | None = None,
    ) -> Cursor[T] | None:
        # if in psycopg mode, replace parameter syntax
        if PSYCOPG_PARAM is not None:
            sql = PSYCOPG_PARAM.sub(r"%(\1)s", sql)

        curs = self.conn.cursor()
        if isinstance(parameters, BaseModel):
            parameters = parameters.dict()
        curs.execute(sql, parameters)
        if output is not None:
            return Cursor(curs, output)
        else:
            return None


@contextlib.contextmanager
def connect() -> Iterator[Interface]:
    # Needs the AURORA_CLUSTER_ARN and AURORA_SECRET_ARN environment variables
    if "AURORA_CLUSTER_ARN" in os.environ and "AURORA_SECRET_ARN" in os.environ:
        with aurora_data_api.connect(database="musicteam") as conn:
            yield Interface(conn)

    # Try pglite
    if not PGLITE_AVAILABLE:
        raise Exception("Aurora connection details not available")

    global PGLITE_MANAGER
    if PGLITE_MANAGER is None:
        if os.path.exists("../instance/pglite_manager.js"):
            os.unlink("../instance/pglite_manager.js")
        config = PGliteConfig(
            work_dir="../instance",
            extensions=[
                "uuid_ossp",
            ],
        )
        PGLITE_MANAGER = PGliteManager(config)

        # monkeypatch pglite to save database to disk
        _orig_content = PGLITE_MANAGER._generate_unix_js_content

        def generate_content(ext_requires_str: str, ext_obj_str: str) -> str:
            content = cast(str, _orig_content(ext_requires_str, ext_obj_str))
            content = content.replace("new PGlite(", 'new PGlite("./datadir", ')
            return content

        PGLITE_MANAGER._generate_unix_js_content = generate_content

        PGLITE_MANAGER.start()

    connstr = PGLITE_MANAGER.get_psycopg_uri()
    with cast(aurora_data_api.AuroraDataAPIClient, psycopg.connect(connstr)) as conn:
        yield Interface(conn)


def ping() -> bool:
    with connect() as conn:
        try:
            conn.execute("SELECT 1;")
            return True
        except Exception:
            return False


def upgrade_to(version: str) -> None:
    with connect() as conn:
        schema_fn = os.path.join(
            os.path.dirname(__file__), f"db-schema/schema-{version}.sql"
        )
        with open(schema_fn) as fp:
            conn.execute(fp.read())
