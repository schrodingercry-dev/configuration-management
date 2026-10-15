#!/bin/bash
set -e
cd "$(dirname "$0")/.."
printf 'exit
' | bash run.sh --script scripts/startup.txt
printf 'exit
' | bash run.sh --vfs vfs/minimal.json
printf 'exit
' | bash run.sh --vfs vfs/several_files.json --script scripts/startup.txt
