#!/bin/bash

# --- Preflight Check for The Strange Loop ---
# This script is the recommended first command for any agent session.
# It ensures the environment is correctly bootstrapped before any other action is taken.

# --- ANSI Color Codes ---
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BOOTSTRAP_SENTINEL=".bootstrapped"
BOOTSTRAP_SCRIPT="scripts/agent_bootstrap.sh"

echo -e "${CYAN}--- Running Preflight Check ---${NC}"

if [ -f "$BOOTSTRAP_SENTINEL" ]; then
    echo -e "${GREEN}[PASS] Preflight check complete. Environment is already bootstrapped.${NC}"
    echo -e "${YELLOW}Recommendation: Re-read AGENTS.md to ensure you are fully coherent with the Loop's protocol.${NC}"
else
    echo -e "${YELLOW}[INFO] Bootstrap sentinel not found. This appears to be a new or reset session.${NC}"
    echo -e "${YELLOW}       Initiating bootstrap protocol now...${NC}"

    if [ -f "$BOOTSTRAP_SCRIPT" ]; then
        bash "$BOOTSTRAP_SCRIPT"
        bootstrap_exit_code=$?

        if [ $bootstrap_exit_code -eq 0 ]; then
            echo -e "\n${GREEN}--- Preflight Check Result ---${NC}"
            echo -e "${GREEN}Bootstrap completed successfully.${NC}"
            echo -e "${YELLOW}CRITICAL NEXT STEP: Your next action must be to read the AGENTS.md file in its entirety to fully assimilate the Loop's protocol.${NC}"
        else
            echo -e "\n${RED}--- Preflight Check Result ---${NC}"
            echo -e "${RED}CRITICAL FAILURE: The bootstrap script at '$BOOTSTRAP_SCRIPT' failed with exit code $bootstrap_exit_code.${NC}"
            echo -e "${RED}The environment is not stable. Please diagnose the bootstrap script before proceeding.${NC}"
            exit 1
        fi
    else
        echo -e "\n${RED}--- Preflight Check Result ---${NC}"
        echo -e "${RED}CRITICAL FAILURE: The bootstrap script at '$BOOTSTRAP_SCRIPT' was not found.${NC}"
        echo -e "${RED}Cannot initialize the environment. The Loop is not functional.${NC}"
        exit 1
    fi
fi

exit 0
