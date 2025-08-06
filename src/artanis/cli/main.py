"""Main CLI entry point for Artanis."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from artanis._version import __version__

from .commands.new import NewCommand


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="artanis",
        description="Artanis - A lightweight, fast ASGI web framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Artanis {__version__}",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )

    # Add 'new' command
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new Artanis project",
        description="Create a new Artanis project with a basic template",
    )

    new_parser.add_argument(
        "project_name",
        help="Name of the project to create",
    )

    new_parser.add_argument(
        "base_directory",
        nargs="?",
        default=".",
        help="Base directory to create the project in (default: current directory)",
    )

    new_parser.add_argument(
        "--venv",
        action="store_true",
        help="Create a virtual environment and install dependencies",
    )

    new_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing files if they exist",
    )

    return parser


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # If no command was provided, show help
    if not parsed_args.command:
        parser.print_help()
        return 1

    try:
        # Execute the appropriate command
        if parsed_args.command == "new":
            command = NewCommand()
            return command.execute(
                project_name=parsed_args.project_name,
                base_directory=parsed_args.base_directory,
                venv=parsed_args.venv,
                force=parsed_args.force,
            )
        print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
