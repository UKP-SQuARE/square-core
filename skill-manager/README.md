# Skill-Manager
The Skill-Manager serves as a central service for interacting with the Skills. It provides a RESTful CRUD (Create, Read, Update, Delete) interface for Skills. All skill information is saved in a [mongoDB](https://www.mongodb.com/) instance. Further, it allows interacting with skills by checking their health, querying them, and changing their public/private status.

## Project Structure
```
├───skill_manager
│   ├───api.py              # definition of endpoints
│   ├───models.py           # input and output of endpoints
│   ├───mongo_model.py      # utility interface for loading data from and to mongoDB
│   ├───mongo_settings.py   # utility class for storing mongoDB connection settings
│   ├───py_object_id.py     # utility class for mongoDB ID
├───tests
│   ├───test_api.py
├───.env                    # environment file loaded by root docker-compose.yaml
├───Dockerfile              # image definition
├───logging.conf            # logging configuration
├───requirements.dev.txt    # dependencies for development
├───requirements.txt        # dependencies
```

## Testing
For running tests locally, please install development dependencies. It is highly recommended to install the package into a separate [virtual environment](https://docs.python.org/3/tutorial/venv.html). Note that tests include integration tests with mongoDB. To run them successfully docker needs to be installed on your system. The test will automatically spin up a mongoDB instance for testing and shut it down at the end of testing.
```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
python -m pytest
```
## Setup
### Environment Configuration
The `.env` file holds the access information to the mongoDB. We recommend running mongoDB through docker.  
The access information for MongoDB has to be configured when starting the service via docker. For example:  
```bash
docker run -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=example mongo
```
In this case, mongoDB will be running on the `localhost` on port `27017`. The root username will be `root`, and the password `example`. For details see the docker hub [mongo](https://hub.docker.com/_/mongo) image description.  
Set the same configuration in the `.env`. For example:
```bash
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
MONGO_HOST=localhost
MONGO_PORT=27017
```
