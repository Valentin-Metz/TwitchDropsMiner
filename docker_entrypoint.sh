#!/bin/bash

printf '%(%Y-%m-%d %H:%M:%S)T: Started new container\n' -1

# Execute every command with the virtual display active
xvfb-run "$@"
