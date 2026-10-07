#!/bin/bash

find . -maxdepth 1 -type f -name "*.$1" -print0 | tar --null -cvf archive.tar -T -
