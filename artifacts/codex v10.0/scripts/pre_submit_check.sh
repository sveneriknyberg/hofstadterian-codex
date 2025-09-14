# scripts/pre_submit_check.sh

#!/bin/bash
# Orchestrates an interactive submission process.

# --- Configuration ---
ARTIFACTS_DIR="artifacts"
HANDOFFS_DIR="handoffs"
WISDOM_PACKET_PREFIX="wisdom_packet_"

echo "--- Initiating Submission Gauntlet ---"

# === STAGE 1: Artifact Verification ===
echo "Verifying handoff artifacts..."
latest_packet=$(find "$ARTIFACTS_DIR" -name "${WISDOM_PACKET_PREFIX}*.json" -mmin -10 -print -quit)
if [ -z "$latest_packet" ]; then
    echo "❌ FAILURE: No recent Wisdom Packet found."
    exit 1
fi

latest_handoff=$(find "$HANDOFFS_DIR" -name "*.md" -mmin -10 -print -quit)
if [ -z "$latest_handoff" ]; then
    echo "❌ FAILURE: No recent human-readable handoff found."
    exit 1
fi
echo "✅ Artifacts verified."

# === STAGE 2: Code Review Mandate ===
echo
echo "--- AGENT ACTION REQUIRED: Code Review ---"
echo "✅ You must now run request_code_review()."
echo "Analyze and address any actionable feedback."

# === STAGE 3: Awaiting Gardener Approval ===
echo
echo "--- WAITING FOR HUMAN REVIEW ---"
read -p "GARDENER (Human): Press ENTER to approve submission..."

# === STAGE 4: Final Submission Clearance ===
echo
echo "✅ Approval received."
echo "--- AGENT ACTION REQUIRED: Submission ---"
echo "You are now cleared to run submit()."
echo

exit 0