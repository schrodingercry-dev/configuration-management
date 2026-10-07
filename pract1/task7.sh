#!/bin/bash

find "$1" -type f -exec md5sum {} + | sort | uniq -w 32 --all-repeated=separate
