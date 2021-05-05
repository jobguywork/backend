psql -v ON_ERROR_STOP=1 --username "jobguy" --dbname "jobguydb"
CREATE DATABASE jgdb;
\q;
psql -v ON_ERROR_STOP=1 --username "jobguy" --dbname "jgdb" < jobguy_db_backup


psql -c "DROP DATABASE jgdb;"
psql -c "CREATE DATABASE jgdb;"
psql -c "CREATE USER jobguy WITH PASSWORD 'db_password';"
psql -c "ALTER ROLE jobguy SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE jobguy SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE jobguy SET timezone TO 'UTC';"
psql -c "ALTER ROLE jobguy SUPERUSER;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE jgdb TO jobguy;"
psql -u jobguy -c "CREATE EXTENSION postgis;"
