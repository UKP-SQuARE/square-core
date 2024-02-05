# Chatbot Rating ​Interface

This component is composed of a Vue.js frontend and a Python FastAPI backend with MongoDB, orchestrated with Docker for the backend services.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker
- Node.js v16

## Installation

### Frontend Setup

1. Clone the frontend repository to your local machine.
2. Navigate to the frontend directory:
    ```sh
    cd frontend
    ```
3. Install the dependencies:
    ```sh
    npm install
    ```
4. Serve the application locally:
    ```sh
    npm run serve
    ```
   The frontend should now be running on [http://localhost:8080](http://localhost:8080).

### Backend Setup

1. Navigate to the Profile-Manager directory:
    ```sh
    cd profile-manager
    ```

Before running the backend services, you need to set up authentication by generating a private key and a token.

2. In the Profile-Manager directory, generate your authentication credentials:
    ```bash
    make auth
    ```
   This command will create a `private_key.pem` file in the root of the project and display a token for testing purposes.

3. Start the backend services using Docker Compose:
    ```sh
    docker-compose up
    ```
   This will set up the FastAPI application and MongoDB, and bind the API to [http://localhost:10000](http://localhost:10000).

Now, both the frontend and backend should be up and running, and you can begin using the Chatbot Rating Platform.


## Development Setup

For development, we use Docker to run MongoDB and to manage our data. The predefined JSON datasets are imported into the Dockerized MongoDB instance for a seamless development experience.


### Importing Predefined Data into MongoDB

1. Navigate to the ```profile-manager``` directory where the `docker-compose.yml` file is located.
2. Start the MongoDB container with the following command:

    ```sh
    docker-compose up
    ```

3. With the MongoDB container running, you can execute `mongoimport` by connecting to the container. First, find the container ID or name of your running MongoDB container with:

    ```sh
    docker ps
    ```

4. Once you have the container ID or name, use the following command to import data:

    ```sh
    docker exec -it <container_id_or_name> mongoimport --db daspChatBotRating --collection Profile --file /data/db/newDaspChatBotRating.Profile.json --jsonArray --authenticationDatabase admin --username root --password mongo-local-pw
    ```

    Replace `<container_id_or_name>` with your MongoDB container's ID or name.

**Note**: The above command assumes that you have the JSON file `newDaspChatBotRating.Profile.json` in the `./mongo_files/db` directory, which is mounted to the container. Adjust the file path if your setup is different.


## Support

If you encounter any issues or require assistance, please open an issue in the repository for support.

