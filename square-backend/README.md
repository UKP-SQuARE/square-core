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
* config.json: The config file with the configuration for Flask, the Flask modules and the server code
* squareapi: the Flask server  
    * skill: Skill selection and request handling
    * app.py: The Flask App
    * api.py: The REST API
    * websocket.py: The WebSocket API
    * models.py: The models used in the database

## Creating a database
Run `python flask-mange.py db init` `python flask-mange.py db migrate` `python flask-mange.py db upgrade` to create a fresh database with all required tables.

`python flask-mange.py shell` starts a Python shell in the app context so you can easily manage the DB manually with it.

## Starting the server
Run `python appserver.py`.

## API Documentation
The API is documented [here](squareapi/api.py) in the docstrings as YAML-formatted Swagger documentation.
The endpoint `/apidocs` of a running server renders the entire documentation as a webpage.
