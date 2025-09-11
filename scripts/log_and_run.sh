#!/bin/bash

# log_and_run.sh (v2)
# This script is a wrapper that executes a command, captures its output,
# constructs a JSON log entry, and passes it to a Python helper script
# for safe appending to the session history file.

# --- Configuration ---
PYTHON_HELPER="scripts/append_to_log.py"

# --- Argument Parsing ---
if [ "$#" -eq 0 ]; then
    exit 0
fi

COMMAND="$1"
COMMAND_BASENAME=$(basename "$COMMAND")
shift
ARGS=("$@")

# --- Execution and Output Capture ---
STDOUT_FILE=$(mktemp)
STDERR_FILE=$(mktemp)
"$COMMAND" "${ARGS[@]}" > "$STDOUT_FILE" 2> "$STDERR_FILE"
EXIT_CODE=$?
STDOUT_CONTENT=$(<"$STDOUT_FILE")
STDERR_CONTENT=$(<"$STDERR_FILE")
rm "$STDOUT_FILE" "$STDERR_FILE"

# --- Hashing ---
if [ -n "$STDOUT_CONTENT" ]; then
    STDOUT_HASH=$(echo -n "$STDOUT_CONTENT" | sha256sum | awk '{print $1}')
else
    STDOUT_HASH=""
fi
if [ -n "$STDERR_CONTENT" ]; then
    STDERR_HASH=$(echo -n "$STDERR_CONTENT" | sha256sum | awk '{print $1}')
else
    STDERR_HASH=""
fi

# --- Status Determination ---
if [ "$EXIT_CODE" -eq 0 ]; then
    STATUS="success"
else
    STATUS="error"
fi

# --- JSON Construction ---
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)
JSON_ARGS=$(python3 -c 'import json, sys; print(json.dumps(sys.argv[1:]))' "${ARGS[@]}")
LOG_ENTRY=$(printf \
    '{"timestamp": "%s", "tool_name": "%s", "tool_args": %s, "status": "%s", "exit_code": %d, "stdout_hash": "%s", "stderr_hash": "%s"}' \
    "$TIMESTAMP" "$COMMAND_BASENAME" "$JSON_ARGS" "$STATUS" "$EXIT_CODE" "$STDOUT_HASH" "$STDERR_HASH"
)

# --- Pass to Python Helper for Safe Writing ---
python3 "$PYTHON_HELPER" "$LOG_ENTRY"

# --- Output to Console ---
if [ -n "$STDOUT_CONTENT" ]; then
    echo "$STDOUT_CONTENT"
fi
if [ -n "$STDERR_CONTENT" ]; then
    >&2 echo "$STDERR_CONTENT"
fi

exit "$EXIT_CODE"
