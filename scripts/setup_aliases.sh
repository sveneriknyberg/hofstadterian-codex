#!/bin/bash

# setup_aliases.sh
# This script defines a set of aliases that wrap common commands with the
# log_and_run.sh wrapper to ensure all actions are logged to .session_history.json.
# This script should be sourced, not executed, e.g., `source scripts/setup_aliases.sh`.

# Determine the absolute path of this script, even when sourced.
# BASH_SOURCE[0] is the path to the script being sourced.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WRAPPER_SCRIPT_PATH="$SCRIPT_DIR/log_and_run.sh"

if [ ! -f "$WRAPPER_SCRIPT_PATH" ]; then
    echo "ERROR: Logger wrapper script not found at '$WRAPPER_SCRIPT_PATH'. Aliases not set."
    return 1
fi

echo "--- Setting up logged command aliases ---"

# --- Core File System & Search ---
alias ls='bash "$WRAPPER_SCRIPT_PATH" ls'
alias grep='bash "$WRAPPER_SCRIPT_PATH" grep'
alias cat='bash "$WRAPPER_SCRIPT_PATH" cat'
alias mv='bash "$WRAPPER_SCRIPT_PATH" mv'
alias cp='bash "$WRAPPER_SCRIPT_PATH" cp'
alias rm='bash "$WRAPPER_SCRIPT_PATH" rm'
alias mkdir='bash "$WRAPPER_SCRIPT_PATH" mkdir'
alias chmod='bash "$WRAPPER_SCRIPT_PATH" chmod'

# --- Execution ---
alias python='bash "$WRAPPER_SCRIPT_PATH" python3' # Alias python to python3 for consistency
alias python3='bash "$WRAPPER_SCRIPT_PATH" python3'
alias bash='bash "$WRAPPER_SCRIPT_PATH" bash'
alias sh='bash "$WRAPPER_SCRIPT_PATH" sh'

# --- Other common tools ---
alias pip='bash "$WRAPPER_SCRIPT_PATH" pip'
alias git='bash "$WRAPPER_SCRIPT_PATH" git'
alias npm='bash "$WRAPPER_SCRIPT_PATH" npm'
alias node='bash "$WRAPPER_SCRIPT_PATH" node'

echo "Aliases set. All aliased commands will now be logged."
echo "If shell seems unresponsive or commands fail unexpectedly, you may need to re-source this file:"
echo "    source scripts/setup_aliases.sh"
