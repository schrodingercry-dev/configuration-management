#!/bin/bash
set -e
cd "$(dirname "$0")/.."
printf 'ls $HOME
cd /tmp
wrong
exit
' | bash run.sh
