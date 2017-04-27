#!/bin/sh

set -e

if [ -n $1 ] && [ "$1" = '-r' ]; then
    rec -q -t sox - | sox -q -p -t raw -c 1 -u -b 8 -r 48000 -
else
    rec -q -t sox - | sox -q -p -t raw -c 1 -u -b 8 -
fi
