"""Minimal UNIX-like shell emulator for practical stages 1-3."""
import argparse
import base64
import binascii
import json
import os
import re
import shlex
import sys
from pathlib import Path

VARIABLE = re.compile(r"\$(\w+|\{[^}]+\})")


def expand_variables(line):
    """Replace environment variables with values from the host OS."""
    def replace(match):
        """Return the value of one referenced environment variable."""
        name = match.group(1).strip("{}")
        return os.environ.get(name, "")

    return VARIABLE.sub(replace, line)


def parse_command(line):
    """Split input into command and arguments after variable expansion."""
    return shlex.split(expand_variables(line))


def execute(line, config):
    """Execute a supported command and return (success, should_exit)."""
    try:
        words = parse_command(line)
    except ValueError as error:
        print(f"Parse error: {error}")
        return False, False
    if not words:
        return True, False
    command, *args = words
    if command in ("ls", "cd"):
        print(f"Command: {command}")
        print(f"Arguments: {args}")
        return True, False
    if command == "conf-dump":
        return dump_config(args, config), False
    if command == "exit":
        if args:
            print("Error: exit does not accept arguments")
            return False, False
        return True, True
    print(f"Unknown command: {command}")
    return False, False


def dump_config(args, config):
    """Display emulator settings in key-value format."""
    if args:
        print("Error: conf-dump does not accept arguments")
        return False
    print(f"vfs_path={config.vfs or ''}")
    print(f"script_path={config.script or ''}")
    return True


def load_vfs(path):
    """Defer loading VFS until stage 3."""
    return {"type": "directory", "children": {}}


def run_script(path, config, prompt):
    """Echo and execute script commands, skipping invalid commands."""
    try:
        with open(path, encoding="utf-8") as source:
            commands = source.readlines()
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Cannot read startup script: {error}") from error
    for line in commands:
        command = line.strip()
        if not command or command.startswith("#"):
            continue
        print(prompt + command)
        _, should_exit = execute(command, config)
        if should_exit:
            return True
    return False


def repl(config, prompt):
    """Read and execute commands until exit or end of input."""
    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        _, should_exit = execute(line, config)
        if should_exit:
            return 0


def main(argv=None):
    """Parse startup options, load VFS and start the emulator."""
    parser = argparse.ArgumentParser(description="Variant 13 shell")
    parser.add_argument("--vfs", help="Path to a JSON VFS")
    parser.add_argument("--script", help="Path to startup commands")
    config = parser.parse_args(argv)
    try:
        load_vfs(config.vfs)
        prompt = f"{Path(config.vfs).stem if config.vfs else 'memory'}> "
        if config.script and run_script(config.script, config, prompt):
            return 0
    except ValueError as error:
        print(f"Startup error: {error}", file=sys.stderr)
        return 1
    return repl(config, prompt)


if __name__ == "__main__":
    sys.exit(main())
