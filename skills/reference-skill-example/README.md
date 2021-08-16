# reference-skill-example
The reference implementation/ template of a skill for SQuARE.  

## Project structure
The server is a FastAPI webserver. Most of the structure can be reused when
making your own skill. Usually only changes in `main.py`, `core`, and `skill` are needed.
```
├───reference-skill-example
│   ├───main.py                 # Entry point for server <--- Change this as needed
│   ├───Dockerfile              # Dockerfile
│   └───skillapi  
│       ├───api                 # API Routes             
│       │   ├───routes
│       ├───core                # Config <--- Change this as needed
│       ├───models              # Input/ output models for API
│       └───skill               # The Skill Logic <--- Change this as needed
```
## Setup
### Installation
This project requires Python >=3.6.  
Install the dependencies with `pip install -r requirements`
### Run locally
1. Create a `.env` file (see [the example](.env.example))
2. `uvicorn inference_server.main:app --reload --host 0.0.0.0 --port 8000 --env-file .env`

Alternatively, for debugging `python main.py` works as well.

####
Install packages with `pip install pytest pytest-cov pytest-asyncio pytest-mock`.
Then run in this folder `pytest`.   
We mock calls to the Model and Data API for the tests with real output of the two APIs.



### Docker
See the [example docker-compose configuration](example_docker-compose.yml).

## Creating your own skill
The following are the steps to follow if you want to create your own skill
based on this reference:
1. Implement your own `predict` function in [here](skillapi/skill/skill.py). 
   There is an example function with helper functions for the Model and Data API that you
   can reuse and adapt as needed. However, you can also write a completely new function.
2. To use a dotenv file (or environment variables) for configuring the server, extend the [config](skillapi/core/config.py) as needed 
and write your own .env file.
3. Write your own [logging.conf](logging.conf) to configure logging as needed.
4. For using different methods for configuring the server and logging and for additional
code that should run when the server is started, change the [main.py](main.py) as needed.