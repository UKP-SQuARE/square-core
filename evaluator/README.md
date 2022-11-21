# Evaluator

*Short description: To be done*

## Project Structure

```
├───evaluator
│   ├───core
│   │   ├───dataset_handler.py              # Handler for retrieval of datasets
│   ├───mongo
│   │   ├───mongo_client.py                 # Wrapper class for (dis-)connecting to mongoDB
│   │   ├───mongo_model.py                  # Utility interface for loading data from and to mongoDB
│   │   ├───py_object_id.py                 # Utility class for mongoDB ID
│   ├───routers
│   │   ├───api.py                          # Main router for all routes with `/api` prefix
│   ├───settings
│   │   ├───keycloak_settings.py            # Settings class for Keycloak, loads .env variables
│   │   ├───dataset_handler_settings.py     # Settings class for the dataset handler 
│   │   ├───mongo_settings.py               # Settings class for MongoDB, loads .env variables
│   ├───auth_utils.py                       # Class for managaing Clients in Keycloak
│   ├───keycloak_api.py                     # Class for managaing Clients in Keycloak
│   ├───main.py                             # main file creatng the `app` object
│   ├───models.py                           # input and output of endpoints
├───tests
│   ├───test_dataset_handler.py             # Tests for dataset-handler
├───.env.template                           # env file template
├───.local.env                              # env file for local deployment
├───.pre-commit-config.yaml                 # pre-commit config           
├───api.http                                # rest client api
├───docker-compose.yaml                     # docker-compose for local deployment
├───Dockerfile                              # image definition
├───logging.conf                            # logging configuration
├───Makefile                                # Makefile
├───pytest.ini                              # pytest config
├───README.md                               # this file
├───requirements.dev.txt                    # dependencies for development
├───requirements.txt                        # dependencies
```

## Local Setup
Create a virtual environment and install the dependencies and development dependencies:

```bash
make install
make install-dev
```

To setup the authentication locally, create a private key and token. The command below will create a file called `private_key.pem` in the root of the project. Furthermore, it will print a token.
```bash
make auth
```
Copy the token and insert it in [`api.http`](./api.http).
```http
@token = eyJ0e...
```

Next, build and bring up the project.
```bash
make build
make up
```
You can see the logs of the skill manager by running:
```bash
make logs
```
You should now be able to interact with the skill manager using the [api.http](./api.http) file, through curl, or via the auto-generated ui at [localhost:8000/docs](http://localhost:8000/docs).

Note, we run `unvicorn` with the `--reload` flag. Whenever you modify your code locally, it will restart the webserver to reflect the latest changes.

## Testing
Tests include integration tests with mongoDB. To run them successfully docker needs to be installed and running on your system. The test will automatically spin up a mongoDB instance for testing and shut it down at the end of testing.
First, make sure the development dependencies are installed:
```bash
make install-dev
```
To run the tests run:
```bash
make test
```

## Contributing
When you install the dev dependenices, also [pre-commit](https://pre-commit.com/) is installed. Before commiting, this will check if all python files are formatted correctly. If not, the commit will be canceled. You can format the codebase by running:
```bash
make format
```
