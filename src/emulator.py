"""Interactive shell prototype for stage 1."""
import os
import re
import shlex

VARIABLE = re.compile(r"\$(\w+|\{[^}]+\})")


def expand_variables(line):
    """Replace references to environment variables."""
    def replace(match):
        """Return the referenced value from the real OS."""
        return os.environ.get(match.group(1).strip("{}"), "")

    return VARIABLE.sub(replace, line)


def parse_command(line):
    """Split the command and arguments after variable expansion."""
    return shlex.split(expand_variables(line))


def execute(line):
    """Handle shell stubs, exit and invalid commands."""
    try:
        words = parse_command(line)
    except ValueError as error:
        print(f"Parse error: {error}")
        return False
    if not words:
        return False
    command, *args = words
    if command in ("ls", "cd"):
        print(f"Command: {command}")
        print(f"Arguments: {args}")
    elif command == "exit" and not args:
        return True
    elif command == "exit":
        print("Error: exit does not accept arguments")
    else:
        print(f"Unknown command: {command}")
    return False


def main():
    """Start the interactive command loop."""
    while True:
        try:
            line = input("memory> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if execute(line):
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
