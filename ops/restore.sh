#!/usr/bin/env bash
set -euo pipefail
FILE="${1:-}"
: "${FILE:?Usage: ./ops/restore.sh BACKUP.dump}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
test -s "$FILE"
echo "WARNING: this restores into $POSTGRES_DB and may overwrite existing data."
docker compose -f docker-compose.production.yml exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$FILE"
echo "Restore completed. Run application smoke tests before reopening traffic."
