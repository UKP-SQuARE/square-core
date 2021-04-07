# Overview
## Core features:
- Questions answering using a pretrained model with no training needed
- Advanced question answering using automatic skill selector, which predicts the best skill that can answer the question
- Provides an overview of your skills and skills that were published by other users
- Develop your own skill and publish on square
- Register, publish, unpublish retrain and delete your skills
\n
## Quick Demo: 
To launch Square, the only prerequisites is docker and docker-compose. docker-compose will build docker containers from scratch install all requirements for you.
1. Install docker and docker-compose
2. Clone Square repository from github
`git clone https://github.com/UKPLab/square-core.git`
3. Launch demo app
`cd square`
`docker-compose up  --build`

## Basic Workflow with pretrained skill 
1. Launch demo app
2. Create a sample skill and launch 
3. Register your sample skill 
4. Choose your sample skill to answer the question 

## For developers
### Developing SQUARE-CORE
- Each module square-backend, square-frontend and reference-skill-example has a README.md, which describes how to start the server individually for your local development
- You can launch all SQUARE-CORE modules at once with docker-composer or individually since each module also have it own Dockerfile so that they can be started, restarted or killed individually. 

### Basic commands

#### Deploy on a remote server and square-core locally
Skill can be deployed on a different server than the SQUARE-CORE, which can create some issues. We has found a work-around solution for this problem.
1. Login to the remote server
2. Get IP of the node with `ifconfig`
3. Start the webserver of the skill
4. On you local machine, create a tunnel to the remote with `ssh -L 5003:$IP:5003 $USERNAME@$HOST` (Note you might need to change the port 5003 to whatever port you are running the skill webserver on).
5. Assert that you can reach the skill from you local machine, e.g. by querying the /ping endpoint. `curl localhost:5003/api/ping`
6. Run square-core with docker-compose
   `docker-compose up`
7. Goto http://localhost and register or login
8. Create a new skill, as URL enter `http://host.docker.internal:5003/api` (Note that currently the form will say the skill is not available, this is a [bug](https://github.com/UKPLab/square-core/issues/8))
9. Go back to home and try your skill.

#### Docker-Compose
Run `docker-compose up [--build]` to run front- and backend along with a Postgres DB in production mode.
This starts no additional skill server.

[docker-compose-skill.yaml](docker-compose-skill.yaml) gives an example on how to add skill server to the cluster.
However, skill server can also be run independently from the core server.  
If a skill server is run in the same cluster, then its container name should be used as host and not 127.0.0.1.
The client will say it is not available, but the backend server can resolve it. 


### System Overview
![Oveview](https://github.com/UKPLab/square-core/blob/master/system.jpg)

__Front-End Application__, web app which currently support two user actions
- receives questions from the user and talks to the square-backend to give the answers
- allows the registration of skills endpoint

__Backend__
- API Service: receives HTTP GET requests containing user queries and forwards them to other system and gives back the answers
- Selector: select skills chosen by the users and get answer from these skills
- ElasticsearchVoteSelector: calculate similarity between question by user and saved questions to decide which skill are relevant automatically

__PostgresDB__: 
- save metadata of registered skills
- save user information
- save examples for training and validation of all skill 

__ElasticSearch__: 
- save examples for training and validation of all skill 

