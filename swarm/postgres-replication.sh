#!/bin/sh
set -e
REPL_PASS="$(cat /run/secrets/postgres_replication_password)"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '$REPL_PASS';
EOSQL
echo "host replication replicator all scram-sha-256" >> "$PGDATA/pg_hba.conf"