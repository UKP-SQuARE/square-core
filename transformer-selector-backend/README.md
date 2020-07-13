# transformer-selector-backend
The backend FastAPI server for the Transformer selector.  
The server manages the storage, loading, training, unpublishing of and inference with the transformer models.  

## Project structure
The project is a FastAPI webserver.
* main.py: The entry point for the server. Can be used directly for dev server or with uvicorn (or other) for production
* config.yaml: The config file with the configuration for FastAPI, the database and the config for model training
* app: the Flask server  
    * transformer: Pytorch model, training, inference, ... code
    * app.py: The FastAPI App
    * api.py: The REST API
    * models.py: The models used in the database

## Square-core Database access required!
The server needs access to the same database that the square-core server uses to have access to the skills and their example sentences.
Model information is persisted there, as well.

## Model storage
The trained Pytorch models are NOT stored in the database but on the file system where the server runs.  
In the config,  `max_num_stored_models` indicates how many models will be stored before the oldest is deleted.

## Limiting threads
When the model is running on GPU, then `max_inference_threads` can be used to limit the number of threads running inference.  
The training thread is NOT included in this count. Please set `max_inference_threads` so that the server can train a model in parallel to regular inference.

## Starting the server
Run `python main.py` for dev server or use Uvicorn or Starlett or something like that for a production server.
