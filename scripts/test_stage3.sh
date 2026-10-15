#!/bin/bash
set -e
cd "$(dirname "$0")/.."
for file in vfs/minimal.json vfs/several_files.json vfs/deep_tree.json; do
  printf '\n=== %s ===\n' "$file"
  printf 'exit
' | bash run.sh --vfs "$file" --script scripts/startup.txt
done
printf '\n=== Missing VFS (expected error) ===\n'
bash run.sh --vfs vfs/missing.json </dev/null && exit 1 || true
printf '\n=== Invalid VFS (expected error) ===\n'
bash run.sh --vfs vfs/invalid.json </dev/null && exit 1 || true
