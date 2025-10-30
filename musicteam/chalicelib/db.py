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
import boto3
from chalicelib.config import AURORA_CLUSTER_ARN
from chalicelib.config import AURORA_SECRET_ARN
from pydantic import BaseModel

DatabaseResumingException = boto3.client(
    "rds-data"
).exceptions.DatabaseResumingException
UndefinedTable = aurora_data_api.PostgreSQLError.from_code("42P01")  # type: ignore[attr-defined]

PSYCOPG_PARAM: re.Pattern[str] | None

try:
    if AURORA_CLUSTER_ARN is not None and AURORA_SECRET_ARN is not None:
        raise ImportError()

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


# increment this whenever a new db schema update is added
DB_VERSION = 1


T = TypeVar("T", bound=BaseModel)


class Cursor(Generic[T]):
    def __init__(self, curs: aurora_data_api.AuroraDataAPICursor, model: type[T]):
        self.curs = curs
        self.model = model

    @property
    def rowcount(self) -> int:
        return self.curs.rowcount

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
    ) -> int: ...

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
    ) -> Cursor[T] | int:
        # if in psycopg mode, replace parameter syntax
        if PSYCOPG_PARAM is not None:
            sql = PSYCOPG_PARAM.sub(r"%(\1)s", sql)

        curs = self.conn.cursor()
        if isinstance(parameters, BaseModel):
            parameters = parameters.model_dump()
        curs.execute(sql, parameters)
        if output is not None:
            return Cursor(curs, output)
        else:
            return curs.rowcount


@contextlib.contextmanager
def connect() -> Iterator[Interface]:
    if AURORA_CLUSTER_ARN and AURORA_SECRET_ARN:
        with aurora_data_api.connect(
            database="musicteam",
            aurora_cluster_arn=AURORA_CLUSTER_ARN,
            secret_arn=AURORA_SECRET_ARN,
        ) as conn:
            yield Interface(conn)
            return

    # Try pglite
    if not PGLITE_AVAILABLE:
        raise Exception("Aurora connection details not available")

    global UndefinedTable
    UndefinedTable = psycopg.errors.UndefinedTable

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


class VersionRow(BaseModel):
    ver: int


def upgrade_db() -> bool:
    with connect() as conn:
        if not conn.execute("SELECT 1 WHERE pg_try_advisory_lock(10010)"):
            return False

        conn.execute(
            "CREATE TABLE IF NOT EXISTS _version (pk TEXT PRIMARY KEY, ver INT)"
        )

        curs = conn.execute(
            "SELECT ver FROM _version WHERE pk = 'db_version'", output=VersionRow
        )
        current_ver = curs.fetchone() or VersionRow(ver=0)

        while current_ver.ver < DB_VERSION:
            next_ver = current_ver.ver + 1
            schema_fn = os.path.join(
                os.path.dirname(__file__), f"db-schema/schema-{next_ver:03d}.sql"
            )
            with open(schema_fn) as fp:
                # todo: more intelligent statement splitting
                for statement in fp.read().split(";"):
                    print(statement)
                    conn.execute(statement)

            curs = conn.execute(
                "SELECT ver FROM _version WHERE pk = 'db_version'", output=VersionRow
            )
            current_ver = curs.fetchone() or VersionRow(ver=0)

        conn.execute("SELECT pg_advisory_unlock_all()")

    return True


def ping() -> bool:
    check_upgrade = False
    with connect() as conn:
        try:
            result = conn.execute(
                "SELECT 1 FROM _version WHERE pk = 'db_version' AND ver = :ver",
                {"ver": DB_VERSION},
            )
            if result == 0:
                raise UndefinedTable()
            return True
        except DatabaseResumingException:
            return False
        except UndefinedTable:
            check_upgrade = True

    if check_upgrade:
        return upgrade_db()

    return True


def upgrade_to(version: str) -> None:
    with connect() as conn:
        schema_fn = os.path.join(
            os.path.dirname(__file__), f"db-schema/schema-{version}.sql"
        )
        with open(schema_fn) as fp:
            conn.execute(fp.read())
