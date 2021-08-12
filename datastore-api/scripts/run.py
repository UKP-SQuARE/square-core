import asyncio
import os
import sys
import time

import requests
from dotenv import load_dotenv


sys.path.append(os.getcwd())

from app.core.generate_package import generate_and_upload_package


load_dotenv(".env")


def check_vespa_config_server():
    url = os.environ.get("VESPA_CONFIG_URL") + "/ApplicationStatus"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def check_vespa_app_server():
    url = os.environ.get("VESPA_APP_URL") + "/ApplicationStatus"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def activate_vespa_app_server():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_and_upload_package())


def _wait_until_true(func, wait_msg, success_msg, timeout_msg, start_func=None, sleep_time=0.5, timeout=60):
    if not func():
        print(wait_msg)
        if start_func:
            start_func()
        start_time = time.time()
        while not func():
            if time.time() - start_time > timeout:
                print(timeout_msg)
                exit(1)
            time.sleep(sleep_time)
    print(success_msg)


def wait_for_vespa_config_server():
    _wait_until_true(
        check_vespa_config_server,
        "Waiting for Vespa config server. Please make sure Vespa has been started...",
        "\u2714 Vespa config server is up.",
        "\u274c Timed out.",
    )


def wait_for_vespa_app_server():
    _wait_until_true(
        check_vespa_config_server,
        "Waiting for Vespa app server to start...",
        "\u2714 Vespa app server is up.",
        "\u274c Timed out.",
        activate_vespa_app_server,
    )


def run(dev=False, port=8000):
    wait_for_vespa_config_server()
    wait_for_vespa_app_server()
    if dev:
        os.system(f"uvicorn app.main:app --port {port} --reload --reload-dir app")
    else:
        os.system(f"uvicorn app.main:app --port {port} --log-config logging.conf")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_wait_vespa = subparsers.add_parser("wait-vespa")
    parser_wait_vespa.add_argument("server", choices=["config", "app"])

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("--dev", action="store_true")
    parser_run.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()
    if args.command == "wait-vespa":
        if args.server == "config":
            wait_for_vespa_config_server()
        elif args.server == "app":
            wait_for_vespa_app_server()
    elif args.command == "run":
        run(dev=args.dev, port=args.port)
