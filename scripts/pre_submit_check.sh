#!/bin/bash

# --- Pre-Submit Check Script (v2) ---
# This script acts as a gatekeeper to ensure the repository is in a
# clean and consistent state before a submission is requested.
# It enforces the Handoff -> Review -> Submit protocol.

echo "--- Running Pre-Submit Checks (v2) ---"

# --- Find the latest handoff file ---
LATEST_HANDOFF_FILE=$(ls -1t handoffs/*.md 2>/dev/null | head -n 1)

if [ -z "$LATEST_HANDOFF_FILE" ]; then
    echo "[1/4] Checking for handoff file..."
    echo "  [FAIL] No handoff files found in the 'handoffs/' directory."
    echo "         Please run 'python3 scripts/create_handoff.py' to document your work."
    exit 1
fi

LATEST_HANDOFF_FILENAME=$(basename "$LATEST_HANDOFF_FILE")

# --- Check 1: Verify the latest handoff has been processed ---
echo "[1/4] Checking if handoff '$LATEST_HANDOFF_FILENAME' is processed..."
if grep -q "$LATEST_HANDOFF_FILENAME" context/history.log; then
    echo "  [PASS] Handoff is present in context/history.log."
else
    echo "  [FAIL] Handoff has not been processed into the Loop's memory."
    echo "         This should have been handled by 'create_handoff.py'. Please check for errors."
    exit 1
fi

# --- Check 2: Verify a code review has been requested for this handoff ---
echo "[2/4] Checking for a new code review request..."
REVIEW_LOG="context/reviews.log"
if [ ! -f "$REVIEW_LOG" ]; then
    echo "  [FAIL] Review log '$REVIEW_LOG' not found."
    echo "         Please run 'bash scripts/request_review.sh' to log your request."
    exit 1
fi

LATEST_HANDOFF_TIME=$(stat -c %Y "$LATEST_HANDOFF_FILE")
REVIEW_LOG_TIME=$(stat -c %Y "$REVIEW_LOG")

if [ "$REVIEW_LOG_TIME" -ge "$LATEST_HANDOFF_TIME" ]; then
    echo "  [PASS] A review has been requested for the latest handoff."
else
    echo "  [FAIL] The review request is older than the latest handoff."
    echo "         Please run 'bash scripts/request_review.sh' again."
    exit 1
fi

# --- Check 3: Verify the Git working directory is clean ---
echo "[3/4] Checking for a clean Git working directory..."
if [ -z "$(git status --porcelain)" ]; then
    echo "  [PASS] Git working directory is clean."
else
    echo "  [FAIL] Git working directory is not clean. Found untracked or modified files:"
    git status --porcelain
    exit 1
fi

# --- Check 4: Run unit tests ---
echo "[4/4] Running unit tests..."
if pytest; then
    echo "  [PASS] All unit tests passed."
else
    echo "  [FAIL] Unit tests failed. Please fix them before submitting."
    exit 1
fi

echo "--- All Pre-Submit Checks Passed ---"
exit 0
