#!/bin/sh

# Script to install all dependencies for the project

# Function to check the exit status of the last command
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}


# Update the system packages
sudo apt update
sudo apt upgrade -y


# install gunicorn
sudo apt-get install gunicorn -y
check_status "Failed to install gunicorn"


# Install Timescaledb dependencies
sudo apt install gnupg postgresql-common apt-transport-https lsb-release wget
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
check_status "Failed to add Timescaledb GPG key"


# Install Timescaledb
sudo apt update
sudo apt install timescaledb-2-postgresql-16 postgresql-client-16 -y
check_status "Failed to update package list"


# Tune timescaledb
sudo timescaledb-tune
check_status "Failed to tune Timescaledb"

# Restart the PostgreSQL service
sudo systemctl restart postgresql
check_status "Failed to restart PostgreSQL service"

# Install the mosquitto broker
sudo apt install -y mosquitto
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Create service file
sudo bash -c 'cat >  /etc/systemd/system/autoswitch.service' << EOF
[Unit]
Description=Loadshedding Autoswitch API
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/Loadshedding_Autoswitch_v1/api
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
check_status "Failed to create service file"

sudo systemctl daemon-reload
check_status "Failed to reload systemd daemon"

# login to psql and create the database
# config username, password in the .env file
# SECRET_KEY='your_secret_key'
# SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://postgres:password@localhost:5433/autoswitch'
# JWT_SECRET_KEY='jwt_secret_key'
# run in psql db -> CREATE EXTENSION IF NOT EXISTS timescaledb;
# then \dx;
# run pip install -r requirements.txt
# To start the service, run:
# sudo systemctl start loadshedding_autoswitch
