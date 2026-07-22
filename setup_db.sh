#!/bin/bash
sudo -u postgres psql -c "CREATE DATABASE palenque_db;"
sudo -u postgres psql -c "CREATE USER palenque_user WITH PASSWORD 'PalenqueFlow2026!';"
sudo -u postgres psql -c "ALTER ROLE palenque_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE palenque_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE palenque_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE palenque_db TO palenque_user;"
sudo -u postgres psql -d palenque_db -c "GRANT ALL ON SCHEMA public TO palenque_user;"
echo "Database setup complete."
