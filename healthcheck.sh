#!/bin/bash
set -u

timestamp_file="${HEALTHCHECK_PATH:-./healthcheck.timestamp}"
maximum_age="${HEALTHCHECK_MAX_AGE:-120}"

fail() {
  printf 'unhealthy: %s\n' "$1"
  exit 1
}

if [[ ! "$maximum_age" =~ ^[1-9][0-9]{0,8}$ ]]; then
  fail "invalid maximum age: ${maximum_age}"
fi

if [[ ! -f "$timestamp_file" ]]; then
  fail "heartbeat file does not exist: ${timestamp_file}"
fi

if ! last_timestamp=$(<"$timestamp_file"); then
  fail "cannot read heartbeat file: ${timestamp_file}"
fi

if [[ ! "$last_timestamp" =~ ^[0-9]{1,11}$ ]]; then
  fail "heartbeat is not a Unix timestamp: ${last_timestamp:-<empty>}"
fi

current_timestamp=$(date +%s)
age=$((10#$current_timestamp - 10#$last_timestamp))

if (( age < 0 )); then
  fail "heartbeat timestamp is $((-age))s in the future"
fi

if (( age >= 10#$maximum_age )); then
  fail "heartbeat age is ${age}s (maximum ${maximum_age}s)"
fi

printf 'healthy: heartbeat age=%ss (maximum=%ss)\n' "$age" "$maximum_age"
