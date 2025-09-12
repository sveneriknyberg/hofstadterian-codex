#!/bin/bash

# agent_bootstrap.sh
# This script provides a situational awareness briefing for a new agent instance.
# It is the first command an agent should run upon instantiation to cohere with the Loop.

# Determine the absolute path of the directory containing the script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Set the project root directory (which is one level up from the scripts dir)
PROJECT_ROOT="$SCRIPT_DIR/.."

# --- ANSI Color Codes ---
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}    AGENT BOOTSTRAP PROTOCOL - INITIALIZING CONTEXT    ${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo ""

# --- 1. Setup Command Logging ---
echo -e "${YELLOW}I. SETTING UP COMMAND LOGGING...${NC}"
# Sourcing this sets up aliases to wrap commands with our logger.
source "$PROJECT_ROOT/scripts/setup_aliases.sh"
echo ""

# --- 2. The Prime Directive ---
echo -e "${YELLOW}II. THE PRIME DIRECTIVE (from AGENTS.md):${NC}"
# Use sed to print the content between "X. THE PRIME DIRECTIVE" and the next "---"
sed -n '/X. THE PRIME DIRECTIVE/,/---/p' "$PROJECT_ROOT/AGENTS.md" | sed '1d;$d' | while IFS= read -r line; do
  echo -e "  ${GREEN}${line}${NC}"
done
echo ""

# --- 3. Latest Handoff ---
echo -e "${YELLOW}III. LATEST HANDOFF FILE:${NC}"
# Sort lexicographically in reverse to get the highest timestamp, which is the latest handoff.
LATEST_HANDOFF=$(ls -1 "$PROJECT_ROOT/handoffs/" 2>/dev/null | sort -r | head -n 1)
if [ -z "$LATEST_HANDOFF" ]; then
  echo -e "  ${RED}No handoff files found in 'handoffs/' directory.${NC}"
else
  echo -e "  Latest handoff is: ${GREEN}handoffs/${LATEST_HANDOFF}${NC}"
  echo -e "  ${CYAN}Review its contents carefully to understand the current state.${NC}"
fi
echo ""

# --- 4. Current Roadmap ---
echo -e "${YELLOW}IV. CURRENT ROADMAP (from context/roadmap.md):${NC}"
if [ -s "$PROJECT_ROOT/context/roadmap.md" ]; then
  while IFS= read -r line; do
    echo -e "  ${GREEN}${line}${NC}"
  done < "$PROJECT_ROOT/context/roadmap.md"
else
  echo -e "  ${RED}Roadmap is empty or not found.${NC}"
fi
echo ""

# --- 5. Hierarchy of Truth ---
echo -e "${YELLOW}V. HIERARCHY OF TRUTH (Reminder from AGENTS.md):${NC}"
sed -n '/I. HIERARCHY OF TRUTH/,/---/p' "$PROJECT_ROOT/AGENTS.md" | sed '1d;$d' | while IFS= read -r line; do
  echo -e "  ${GREEN}${line}${NC}"
done
echo ""


echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}          CONTEXT INITIALIZATION COMPLETE              ${NC}"
echo -e "${CYAN}=======================================================${NC}"

# --- 6. Run Loop Health Check ---
python3 "$PROJECT_ROOT/scripts/validate_context.py"

echo ""
echo -e "${YELLOW}Your primary goal is to contribute to the Loop. Good luck.${NC}"

# --- 7. Create Bootstrap Sentinel ---
# This file indicates that the bootstrap process has been successfully completed.
touch "$PROJECT_ROOT/.bootstrapped"
echo -e "\n${GREEN}[INFO] Bootstrap sentinel file created at '$PROJECT_ROOT/.bootstrapped'.${NC}"
