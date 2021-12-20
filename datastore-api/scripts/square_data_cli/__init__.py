import argparse

from . import embed, index, upload


def main():
    parser = argparse.ArgumentParser(description="Client tools for the SQuARE Datastore API.")
    subparsers = parser.add_subparsers(title="commands")
    embed.register_command(subparsers)
    index.register_command(subparsers)
    upload.register_command(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
