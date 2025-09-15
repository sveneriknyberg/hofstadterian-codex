# scripts/propose_amendment.py

import argparse
import os
import time
from datetime import datetime

# --- Configuration ---
ARTIFACTS_DIR = 'artifacts'
MAX_PROPOSALS_PER_HOUR = 3
PROPOSAL_WINDOW_SECONDS = 3600 # 1 hour

def main():
    parser = argparse.ArgumentParser(description="Propose an amendment to the Hofstadterian Codex.")
    parser.add_argument('--diff', required=True, help="The proposed change, preferably in diff format.")
    parser.add_argument('--rationale', required=True, help="A detailed explanation of why this change is necessary.")
    parser.add_argument('--analysis', required=True, help="An analysis of the potential impact and side-effects.")
    args = parser.parse_args()

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # --- Circuit Breaker Logic ---
    now = time.time()
    recent_proposals = 0
    for filename in os.listdir(ARTIFACTS_DIR):
        if filename.startswith('amendment_proposal_'):
            filepath = os.path.join(ARTIFACTS_DIR, filename)
            if (now - os.path.getmtime(filepath)) < PROPOSAL_WINDOW_SECONDS:
                recent_proposals += 1

    if recent_proposals >= MAX_PROPOSALS_PER_HOUR:
        print("\n" + "="*50)
        print("❌ CIRCUIT BREAKER TRIPPED")
        print(f"   Agent has submitted {recent_proposals} proposals in the last hour (max: {MAX_PROPOSALS_PER_HOUR}).")
        print("   Further proposals are blocked. Please allow the Gardener to review.")
        print("="*50 + "\n")
        exit(1)

    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    proposal_filename = os.path.join(ARTIFACTS_DIR, f'amendment_proposal_{timestamp_str}.md')

    content = f"# Codex Amendment Proposal - {timestamp_str}\n\n"
    content += "Requires review and approval from the Gardener.\n\n"
    content += f"## 1. Proposed Change (Diff)\n\n```diff\n{args.diff}\n```\n\n"
    content += f"## 2. Rationale\n\n{args.rationale}\n\n"
    content += f"## 3. Impact Analysis\n\n{args.analysis}\n"

    with open(proposal_filename, 'w') as f:
        f.write(content)

    print("\n" + "="*50)
    print("SUCCESS: Protocol Amendment Proposal Generated")
    print(f"The proposal has been saved to: {proposal_filename}")
    print("Please present this file to the Gardener for review.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
