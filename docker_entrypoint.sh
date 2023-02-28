#!/bin/bash

printf '%(%Y-%m-%d %H:%M:%S)T: Started new container\n' -1

# Start X virtual framebuffer
export DISPLAY=:1
Xvfb :1 -screen 0 640x480x8 -nolisten tcp &

# Execute CMDs
"$@"

printf '%(%Y-%m-%d %H:%M:%S)T: Stopped container\n' -1
