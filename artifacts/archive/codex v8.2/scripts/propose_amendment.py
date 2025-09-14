# scripts/propose_amendment.py

import argparse
import os
from datetime import datetime

ARTIFACTS_DIR = 'artifacts'

def main():
    """
    Generates a formal proposal to amend the Hofstadterian Codex.
    """
    parser = argparse.ArgumentParser(
        description="Propose an amendment to the Hofstadterian Codex."
    )
    parser.add_argument(
        '--diff',
        required=True,
        help="The proposed change, preferably in diff format."
    )
    parser.add_argument(
        '--rationale',
        required=True,
        help="A detailed explanation of why this change is necessary."
    )
    parser.add_argument(
        '--analysis',
        required=True,
        help="An analysis of the potential impact and side-effects."
    )
    args = parser.parse_args()

    # Create artifacts directory if it doesn't exist
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    proposal_filename = os.path.join(
        ARTIFACTS_DIR,
        f'amendment_proposal_{timestamp_str}.md'
    )
    
    # Create the proposal content
    content = f"# Codex Amendment Proposal - {timestamp_str}\n\n"
    content += "This is a formal proposal to amend the Hofstadterian Codex. It requires review and approval from the Gardener.\n\n"
    content += "## 1. Proposed Change (Diff)\n\n"
    content += "```diff\n"
    content += f"{args.diff}\n"
    content += "```\n\n"
    content += "## 2. Rationale\n\n"
    content += f"{args.rationale}\n\n"
    content += "## 3. Impact Analysis\n\n"
    content += f"{args.analysis}\n"
    
    # Write the proposal file
    with open(proposal_filename, 'w') as f:
        f.write(content)

    print("\n" + "="*50)
    print("SUCCESS: Protocol Amendment Proposal Generated")
    print(f"The proposal has been saved to: {proposal_filename}")
    print("Please present this file to the Gardener for review.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()