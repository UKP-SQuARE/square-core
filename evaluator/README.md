# Evaluator

*Short description: To be done*

## Project Structure

*To be done*

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
