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


def validate_node(node):
    """Check the JSON VFS tree, including base64 file contents."""
    if not isinstance(node, dict):
        raise ValueError("VFS node must be a JSON object")
    if node.get("type") == "directory":
        validate_directory(node)
    elif node.get("type") == "file":
        validate_file(node)
    else:
        raise ValueError("Unknown VFS node type")


def validate_directory(node):
    """Validate a directory and all of its children recursively."""
    children = node.get("children")
    if not isinstance(children, dict):
        raise ValueError("Directory requires a children object")
    for name, child in children.items():
        if not name or "/" in name or name in (".", ".."):
            raise ValueError("Invalid VFS entry name")
        validate_node(child)


def validate_file(node):
    """Check that a file contains valid base64-encoded bytes."""
    encoded = node.get("content_base64")
    if not isinstance(encoded, str):
        raise ValueError("File requires content_base64 string")
    try:
        base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("Invalid base64 file content") from error


def load_vfs(path):
    """Read a JSON VFS into memory without changing the source file."""
    if not path:
        return {"type": "directory", "children": {}}
    try:
        with open(path, encoding="utf-8") as source:
            data = json.load(source)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot load VFS: {error}") from error
    validate_node(data)
    if data["type"] != "directory":
        raise ValueError("VFS root must be a directory")
    return data


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
