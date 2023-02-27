#!/bin/bash

printf '%(%Y-%m-%d %H:%M:%S)T: Started new container\n' -1
sleep 3

# Execute every command with the virtual display active
xvfb-run "$@"
