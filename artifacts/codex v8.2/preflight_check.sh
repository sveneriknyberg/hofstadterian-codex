# preflight_check.sh

#!/bin/bash

# preflight_check.sh v2.0
# Verifies the environment and issues a startup briefing to the agent.

# --- Configuration & State ---
REQUIRED_DIRS=("scripts" "artifacts" "handoffs")
REQUIRED_SCRIPTS=(
    "scripts/intent_executor.py"
    "scripts/consolidate_handoff.py"
    "scripts/pre_submit_check.sh"
)
SESSION_LOG_FILE=".session_actions.json"
WISDOM_PACKET_PREFIX="wisdom_packet_"
FAIL_FLAG=0

echo "--- Running Pre-Flight System Check ---"

# --- 1. Verify Directory Structure ---
echo
echo "Checking for required directories..."
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "⚠️  Directory '$dir' not found. Creating it now."
        mkdir -p "$dir"
    else
        echo "✅ Directory '$dir' exists."
    fi
done

# --- 2. Verify Core Scripts ---
echo
echo "Checking for core protocol scripts..."
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -f "$script" ]; then
        echo "❌ FAILURE: Core script '$script' is missing."
        FAIL_FLAG=1
    else
        echo "✅ Core script '$script' is present. Ensuring it is executable."
        chmod +x "$script"
    fi
done

# --- 3. Check for Python Dependency ---
echo
echo "Checking for dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ FAILURE: python3 is not found in PATH."
    FAIL_FLAG=1
else
    echo "✅ Dependency 'python3' is available."
fi

# --- 4. Ensure Clean Session State ---
echo
echo "Checking for clean session state..."
if [ -f "$SESSION_LOG_FILE" ]; then
    echo "⚠️  WARNING: An old session log ('$SESSION_LOG_FILE') was found."
    echo "          Please archive or delete this file to ensure a clean start."
    FAIL_FLAG=1
else
    echo "✅ Session state is clean."
fi

# --- 5. Final Briefing for Agent ---
echo
echo "Issuing startup briefing for the agent..."
if [ $FAIL_FLAG -eq 0 ]; then
    echo "--- AGENT BRIEFING ---"
    echo "1. Read your core protocol in AGENTS.md to ensure compliance."
    
    # Find the most recent wisdom packet
    latest_packet=$(ls -t artifacts/${WISDOM_PACKET_PREFIX}*.json 2>/dev/null | head -n 1)

    if [ -z "$latest_packet" ]; then
        echo "2. ℹ️  No previous Wisdom Packet found. You will establish the first one."
    else
        echo "2. Review the last session's context in: $(basename "$latest_packet")"
    fi
    echo "----------------------"
fi

# --- Final Summary ---
echo
echo "-------------------------------------"
if [ $FAIL_FLAG -eq 1 ]; then
    echo "❌ PRE-FLIGHT CHECK FAILED."
    echo "   Please address the issues above before starting the agent session."
    exit 1
else
    echo "✅ System is Nominal. Ready for Agent Session. 🚀"
    exit 0
fi