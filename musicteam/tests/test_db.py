import os
import subprocess

import pytest
from psycopg.errors import UndefinedTable


def test_upgrade_db(monkeypatch, db, tmp_path, snapshot):
    monkeypatch.setattr(db, "INSTANCE_DIR", str(tmp_path))

    with db.connect() as conn:
        with pytest.raises(UndefinedTable):
            conn.execute("SELECT * FROM _version")

    db.upgrade_db()

    assert str(tmp_path) == db.INSTANCE_DIR

    print(db.INSTANCE_DIR)
    with open(os.path.join(db.INSTANCE_DIR, "pgdump.mjs"), "w") as fp:
        fp.write("""
import { PGlite } from '@electric-sql/pglite';
import { pgDump } from '@electric-sql/pglite-tools/pg_dump';
import { uuid_ossp } from '@electric-sql/pglite/contrib/uuid_ossp';
import { vector } from '@electric-sql/pglite-pgvector';

const pg = await PGlite.create({
    dataDir: "./datadir",
    extensions: { uuid_ossp: uuid_ossp, vector: vector }
});

const dump = await pgDump({ pg, args: ['-O'] });
const dumpContent = await dump.text();
console.log(dumpContent);
await pg.close();
            """)

    subprocess.run(
        [
            "npm",
            "install",
            "@electric-sql/pglite@0.5.8",
            "@electric-sql/pglite-socket@0.2.11",
            "@electric-sql/pglite-tools@0.4.8",
            "@electric-sql/pglite-pgvector@0.0.9",
        ],
        cwd=tmp_path,
        check=True,
    )
    result = subprocess.run(["node", "pgdump.mjs"], cwd=tmp_path, capture_output=True)
    print(result.stderr.decode())
    assert result.returncode == 0
    assert result.stdout.decode() == snapshot
