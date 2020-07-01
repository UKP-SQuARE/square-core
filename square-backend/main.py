import eventlet
eventlet.monkey_patch()
from api.app import create_app
import argparse
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--config", type=str, default="./config.yaml")
    parser.add_argument("--logging_config", type=str, default="./logging_config.yaml")
    args = parser.parse_args()

    socketio, app = create_app(config_path=args.config, logging_config_path=args.logging_config)

    socketio.run(app, host=args.host, log_output=True, log=logging.getLogger("server"))
