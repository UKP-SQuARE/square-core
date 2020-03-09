#! /usr/bin/env sh
set -e

echo "Waiting 10s for DB to start"
sleep 10;
python flask-manage.py db migrate
python flask-manage.py db upgrade

echo "Starting the server"
python main.py --host "0.0.0.0"