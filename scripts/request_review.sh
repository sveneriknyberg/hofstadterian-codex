#!/bin/bash
# This script formally requests a code review by logging the request
# to a persistent file in the context directory.

REVIEW_LOG="context/reviews.log"

# Ensure the log file exists
touch "$REVIEW_LOG"

# Append a timestamped request entry
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "$TIMESTAMP - Review Requested" >> "$REVIEW_LOG"

echo "Review request has been logged to $REVIEW_LOG."
echo "You may now proceed with the 'request_code_review' tool to get feedback."
