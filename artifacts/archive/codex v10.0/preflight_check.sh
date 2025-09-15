# preflight_check.sh

#!/bin/bash
# v4.0: Pure validation script.

# --- Configuration ---
EXPECTED_PROTOCOL_VERSION="10.0"
REQUIRED_DIRS=("scripts" "artifacts" "handoffs" "artifacts/archive")
REQUIRED_SCRIPTS=(
    "scripts/intent_executor.py"
    "scripts/consolidate_handoff.py"
    "scripts/pre_submit_check.sh"
    "scripts/propose_amendment.py"
    "scripts/bootstrap_session.py"
)
SESSION_LOG_FILE=".session_actions.json"
FAIL_FLAG=0

echo "--- Running Pre-Flight System Check v4.0 ---"

# --- 1. Verify Protocol Version from AGENTS.md ---
echo
echo "Verifying protocol version..."
if [ ! -f "AGENTS.md" ]; then
    echo "❌ FAILURE: AGENTS.md not found."
    FAIL_FLAG=1
else
    read_version=$(grep -oP '(?<=protocol_version: )[0-9.]+' AGENTS.md)
    if [ "$read_version" == "$EXPECTED_PROTOCOL_VERSION" ]; then
        echo "✅ Protocol version is correct ($EXPECTED_PROTOCOL_VERSION)."
    else
        echo "❌ FAILURE: Protocol version mismatch. Expected '$EXPECTED_PROTOCOL_VERSION', found '$read_version'."
        FAIL_FLAG=1
    fi
fi

# --- 2. Verify Directory Structure ---
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

# --- 3. Verify Core Scripts ---
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

# --- 4. Check for Python Dependency ---
echo
echo "Checking for dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ FAILURE: python3 is not found in PATH."
    FAIL_FLAG=1
else
    echo "✅ Dependency 'python3' is available."
fi

# --- 5. Verify Clean State ---
echo
echo "Checking for clean session state..."
if [ -f "$SESSION_LOG_FILE" ]; then
    echo "❌ FAILURE: An old session log ('$SESSION_LOG_FILE') was found."
    echo "          Please archive or delete this file before starting a new session."
    FAIL_FLAG=1
else
    echo "✅ Session state is clean."
fi

# --- 6. Verify Last Handoff Integrity (Checksum) ---
echo
echo "Verifying integrity of last handoff..."
latest_handoff=$(ls -t handoffs/*.md 2>/dev/null | head -n 1)
if [ -z "$latest_handoff" ]; then
    echo "ℹ️  No previous handoff to verify."
else
    timestamp=$(basename "$latest_handoff" .md)
    wisdom_packet="artifacts/wisdom_packet_$timestamp.json"
    if [ ! -f "$wisdom_packet" ]; then
        echo "⚠️  WARNING: Handoff '$latest_handoff' exists, but corresponding Wisdom Packet is missing."
    else
        expected_sha=$(grep -oP '(?<=SHA256: `)[a-f0-9]+' "$latest_handoff")
        actual_sha=$(sha256sum "$wisdom_packet" | awk '{print $1}')
        if [ "$expected_sha" == "$actual_sha" ]; then
            echo "✅ Last handoff integrity verified for '$wisdom_packet'."
        else
            echo "❌ FAILURE: Checksum mismatch for '$wisdom_packet'. The artifact may be corrupt."
            FAIL_FLAG=1
        fi
    fi
fi

# --- Final Summary ---
echo
if [ $FAIL_FLAG -eq 1 ]; then
    echo "❌ PRE-FLIGHT CHECK FAILED."
    exit 1
else
    exit 0
fi