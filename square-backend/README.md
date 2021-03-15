# square-backend
The backend Flask server for SQuARE.  
The server manages accounts and skills including access rights to them and handles the selection of skills for questions.

The server is run with [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/) using [eventlet](http://eventlet.net/).  
Authentication is performed with JWTs.

Most actions are done with REST endpoints. Querying can be done both via endpoint (then the result is returned once all skills have answered)
or with Websockets (then results are returned one by one as the skills answer).
## Project structure
The project is a Flask webserver.
* flask-manage.py: Managing the database with Flask Migration
* main.py: The entry point for the dev server
* config.yaml: The config file with the configuration for Flask, the Flask modules and the server code
* squareapi: the Flask server  
    * skill: Skill selection and request handling
    * app.py: The Flask App
    * api.py: The REST API
    * websocket.py: The WebSocket API
    * models.py: The models used in the database

## Creating a database
Run `python flask_manage.py db init` `python flask_manage.py db migrate` `python flask-mange.py db upgrade` to create a fresh database with all required tables.

`python flask-manage.py shell` starts a Python shell in the app context so you can easily manage the DB manually with it.

## Starting the server
Run `python main.py`.

## Postgres
Run `docker exec -it square-core_db_1 psql -U square` to access the postgres container
and then use psql command to inspect the db.

## API Documentation
The API is documented [here](squareapi/api.py) in the docstrings as YAML-formatted Swagger documentation.
The endpoint `/apidocs` of a running server renders the entire documentation as a webpage.

## BACKEND DEBUG 
Besides setting DEBUG=True, please add these following line to be able to print to console  
`print("whatever you want print")`  
`import sys`  
`sys.stdout.flush() `  
