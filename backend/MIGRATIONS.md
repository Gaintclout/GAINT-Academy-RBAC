# Database migrations

GAINT Academy now uses Alembic for schema migrations.

From the `backend` directory:

```bash
pip install -r requirements.txt
alembic upgrade head
```

For a new schema change:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The first migration creates the student fee ledger/payment tables when absent and converts existing finance amount columns to `NUMERIC(12,2)` when those tables already exist.

## Existing databases

Before the first production migration, take a database backup. If an existing database was previously created entirely through `Base.metadata.create_all()`, verify it in UAT before applying the migration in production. Do not delete the existing database to adopt Alembic.
