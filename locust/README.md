# Locust
We use Locust for load testing.
See their [documentation](https://docs.locust.io/en/stable/) for more infos.

## Setup
1. Install Python (>3.6) and Locust ([requirements.txt](requirements.txt)) on your system 
   (does not have to be the same system as where the Skill API runs). 
2. Write your ``config.json`` (see below for more)
3. Start the API servers (with Docker or locally or however you want). This does *not* have to be
on the same computer/ server as Locust.
4. Start the Locust server in this directory (``locust -f locustfile.py``), visit the web UI and start 
the load test. For alternative methods see the above documentation.
   
## config.json
We describe the keys with expected values for the config.json:
```json
{
  "config": {
    # Time each user waits (min, max) after a request. Default [1, 2]
    "wait_time": [1, 2],
  },
  # List of Locust tasks. A user randomly selects from this list each time and starts the request
  "tasks": [
    {
      # task name
      "name": "boolq",
      # base URL for skills
      "base_uri": "/api/skill-manager/skill",
      # Request to base_uri/${skill_id}/${endpoint} 
      "endpoint": "query",
      "skill_id": "620bce65df4b0d6e0a02702e",
      # Set to integer greater 1 to increase chance that this task is chosen.
      # This task appears $weight-times in the list of tasks 
      # (from which the next task is uniformly chosen)
      "weight": 1,
      # The JSON of the query that is sent to the Skill API.
      # See the documentation of the API for more details on this.
      "query_json": {
          "query": "Has the UK been hit by a hurricane?",
          "skill_args":
              {
                "context": "The Great Storm of 1987 was a violent extratropical cyclone which caused casualties in England."
              },
          "num_results": 10,
          "user_id": "context"
      }
    }
  ]
}
```
