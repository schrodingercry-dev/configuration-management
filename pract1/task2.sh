#!/bin/bash

awk '!/^#/ && NF >= 2 {print $2, $1}' /etc/protocols | sort -nr | head -n 5
