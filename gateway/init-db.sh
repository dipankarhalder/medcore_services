#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE medcore_admin_auth;
    CREATE DATABASE medcore_patient_auth;
    CREATE DATABASE medcore_profiles;
    CREATE DATABASE medcore_notifications;
EOSQL
