import argparse
import os
from datetime import datetime, timezone

PROPOSAL_FILENAME_PREFIX = "amendment_proposal_"
ARTIFACTS_DIR = "artifacts"

def main():
    parser = argparse.ArgumentParser(description="Propose an amendment to the Hofstadterian Codex.")
    parser.add_argument('--diff', required=True, help="The proposed change, in diff format.")
    parser.add_argument('--rationale', required=True, help="A detailed explanation of why this change is necessary.")
    args = parser.parse_args()

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    proposal_filename = os.path.join(ARTIFACTS_DIR, f"{PROPOSAL_FILENAME_PREFIX}{timestamp_str}.md")

    content = f"# Codex Amendment Proposal - {timestamp_str}\n\n"
    content += "Requires review and approval from the Gardener.\n\n"
    content += f"## 1. Proposed Change (Diff)\n\n```diff\n{args.diff}\n```\n\n"
    content += f"## 2. Rationale\n\n{args.rationale}\n"

    with open(proposal_filename, 'w') as f:
        f.write(content)

    print(f"Success: Protocol Amendment Proposal generated at {proposal_filename}")

if __name__ == "__main__":
    main()
