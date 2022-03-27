export name="datastore-api-base"

docker cp ./requirements.dev.txt $name:/app
docker exec $name pip install -r /app/requirements.dev.txt

docker cp ./tests $name:/app/tests
docker cp ./.env.test $name:/app/.env

docker cp ./pytest.ini $name:/app/pytest.ini
docker exec $name mkdir /app/test-reports
