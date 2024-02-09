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
    ```sh
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

## Postman Documentation

To interact with our backend, the following [Postman CRUD calls](https://documenter.getpostman.com/view/30936078/2s9YywezKv) are available. This collection includes all necessary requests to test and interact with the API, providing a convenient way to understand and use the various endpoints.

## Known Issues
- **Certificate Buttons in Modal View**: In the frontend interface, within the modal view for certificates, there are bugs affecting the functionality of the "Share on Facebook," "Share on LinkedIn," and "Download" buttons. 
- **Backend Queries Performance**: The backend queries are not optimized for handling a large number of entries, which may lead to issues.
- **Points Spending During Unlock**: There is an issue where users can spend an excessive amount of points on unlocking a single LLM.
- **API Design**: The Backend API does not fully adhere to RESTful principles. This could affect the scalability and maintainability of the API.
- **Badge Earning Logic**: The logic for earning badges is currently hardcoded, which limits flexibility and dynamic badge assignment based on user actions or achievements.

## Development Hints

This section provides some useful hints and tips for developers looking to extend the application, work with configurations, or manage the database.

### Working with YAML and Environment Variables

1. **YAML Configuration**: YAML files are used for various configurations, including initial data loading. When modifying YAML files, maintain the correct structure and ensure all necessary fields are included. Currently the YAML files are loaded as is into the respective MongoDB collection. This means when you want to include more functionality into the YAML files, you need first adapt the loading into the pydantic objects. The YAML files are located at `mongo_files/db`. 

2. **Environment Variables**: The application uses environment variables for configuration (e.g., database connection settings). These are set in `.env` files or equivalent. Always check these settings before deployment. `.env` files are mostly used in the `/frontend`

3. **Sensitive Data**: Avoid committing sensitive data (like API keys or database credentials) into the repository. Use environment variables for such data.

### MongoDB Management

1. **Schema Changes**: When modifying the MongoDB schema, ensure that changes are compatible with existing data structures. Update the Pydantic models accordingly.

2. **Data Import/Export**: Use `mongoimport` and `mongoexport` for importing and exporting data. This is useful for setting up development environments or backup purposes.

3. **Database Indexing**: For performance optimization, especially with large datasets, consider adding indexes to your MongoDB collections.

4. **Testing**: When adding new features or making changes to the database schema, ensure thorough testing to avoid data corruption or loss.
E.g. you could use json files for Mock-Data in your Database as we also used (see section `Importing Predefined Data into MongoDB`)

## Support

If you encounter any issues or require assistance, please open an issue in the repository for support.

