#!/bin/bash

timestamp_file="./healthcheck.timestamp"
maximum_age=300

# Check if the timestamp file exists
if [[ ! -f "$timestamp_file" ]]; then
  echo "Timestamp file does not exist."
  exit 1
fi

# Read the timestamp from the file
last_timestamp=$(cat "$timestamp_file")

# Get the current Unix timestamp
current_timestamp=$(date +%s)

# Calculate the difference in seconds
difference=$((current_timestamp - last_timestamp))

# Check if the difference is less than the maximum_age
if [[ $difference -lt $maximum_age ]]; then
  exit 0
else
  exit 1
fi
