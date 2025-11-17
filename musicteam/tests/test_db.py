import os
import subprocess

import pytest
from psycopg.errors import UndefinedTable


def test_upgrade_db(db, tmp_path, snapshot):
    with db.connect() as conn:
        with pytest.raises(UndefinedTable):
            conn.execute("SELECT * FROM _version")

    db.upgrade_db()

    assert str(tmp_path) == db.INSTANCE_DIR

    with open(os.path.join(db.INSTANCE_DIR, "pgdump.mjs"), "w") as fp:
        fp.write(
            """
import { PGlite } from '@electric-sql/pglite';
import { pgDump } from '@electric-sql/pglite-tools/pg_dump';
import { uuid_ossp } from '@electric-sql/pglite/contrib/uuid_ossp';

const pg = await PGlite.create({
    dataDir: "./datadir",
    extensions: { uuid_ossp: uuid_ossp }
});

const dump = await pgDump({ pg, args: ['-O'] });
const dumpContent = await dump.text();
console.log(dumpContent)
            """
        )

    subprocess.run(
        [
            "npm",
            "install",
            "@electric-sql/pglite@0.3.14",
            "@electric-sql/pglite-socket@0.0.19",
            "@electric-sql/pglite-tools@0.2.19",
        ],
        cwd=tmp_path,
        check=True,
    )
    result = subprocess.run(["node", "pgdump.mjs"], cwd=tmp_path, capture_output=True)
    print(result.stderr.decode())
    assert result.returncode == 0
    assert result.stdout.decode() == snapshot
