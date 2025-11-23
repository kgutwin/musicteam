# PostgreSQL Database Schema

This contains the database migrations needed to set up a fresh
MusicTeam database instance, or to upgrade an existing instance to the
latest version.

## The Final Schema

If you're looking for what the final database schema looks like, check
[test_db.ambr](../../tests/__snapshots__/test_db.ambr) in the test snapshots.

## Adding a new schema migration

1. Create the new sequentially numbered schema file (`schema-nnn.sql`)

2. Ensure that the new file contains the following line at the end,
   replacing `<nnn>` with the new version number:

```sql
UPDATE _version SET ver = <nnn> WHERE pk = 'db_version';
```

3. Edit `../db.py` and change the `DB_VERSION` variable to the new
   version number.
