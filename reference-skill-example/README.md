# reference-skill-example
The reference implementation of a skill for SQuARE.  
It showcases all required endpoints with all possible returnable results.

## Project structure
The project is a Flask webserver.
* main.py: The entry point for the dev server
* config.json: The config file with the configuration for Flask, the Flask modules and the server code
* skillapi: the Flask server  
    * app.py: The Flask App
    * api.py: The skill API

## Starting the server
Run `python appserver.py`.

## API Documentation
The JSON format for the API is documented implicitly [in square-backend for the /query endpoint](../square-backend/squareapi/api.py) in the docstrings as YAML-formatted Swagger documentation.
The backend server forwards the query to the skill server with the options untouched.

## Creating your own skill
This reference skill can be used as basis for your own skill. Simply copy the folder and adapt [query()](skillapi/api.py) as needed.