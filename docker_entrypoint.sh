#!/bin/bash
set -eu

printf '%(%Y-%m-%d %H:%M:%S)T: Started new container\n' -1

heartbeat_path="${HEALTHCHECK_PATH:-./healthcheck.timestamp}"
rm -f -- "$heartbeat_path"

# Start X virtual framebuffer
export DISPLAY=:1
rm -f /tmp/.X1-lock
Xvfb :1 -screen 0 640x480x8 -nolisten tcp &

exec "$@"
