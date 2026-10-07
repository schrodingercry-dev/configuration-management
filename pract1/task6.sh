#!/bin/bash

find "${1:-.}" -type f \( -name '*.c' -o -name '*.js' -o -name '*.py' \) -print0 |
while IFS= read -r -d '' file; do
    first_line=$(head -n 1 "$file")

    case "$file" in
        *.c|*.js) pattern='^[[:space:]]*(//|/\*)' ;;
        *.py)      pattern='^[[:space:]]*#' ;;
    esac

    if [[ $first_line =~ $pattern ]]; then
        echo "$file: комментарий есть"
    else
        echo "$file: комментария нет"
    fi
done
