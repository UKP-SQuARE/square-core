#! /usr/bin/env sh
set -e


echo "Waiting 10s for DB to start"
sleep 10;

python flask-manage.py db init --directory=migration
python flask-manage.py db migrate --directory=migration
python flask-manage.py db upgrade --directory=migration

echo "Starting the server"
python main.py --host "0.0.0.0" --logging_conf logging.conf
