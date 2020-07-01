from app.app import create_app
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=5005)
parser.add_argument("--config", type=str, default="./config.yaml")
parser.add_argument("--logging_config", type=str, default="./logging_config.yaml")
args = parser.parse_args()

app = create_app(config_path=args.config, logging_config_path=args.logging_config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port)