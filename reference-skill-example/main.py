from skillapi.app import create_app
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--config", type=str, default="./config.yaml")
    parser.add_argument("--logging_config", type=str, default="./logging_config.yaml")
    args = parser.parse_args()
    app = create_app(config_path=args.config, logging_config_path=args.logging_config)
    app.run(port=8080)
else:
    app = create_app(config_path=os.environ.get("CONFIG", "./config.yaml"), logging_config_path=os.environ.get("LOGGING_CONFIG", "./logging_config.yaml"))
    app.run(port=8080)
