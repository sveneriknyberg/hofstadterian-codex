# scripts/propose_amendment.py
# v14.2: Creates a structured JSON file for a protocol amendment proposal.

import argparse
import json
import os
from datetime import datetime, timezone

AMENDMENTS_DIR = 'context/amendments'

def main():
    parser = argparse.ArgumentParser(description="Propose a protocol amendment.")
    parser.add_argument("--target-file", required=True, help="The protocol file to be amended (e.g., 'scripts/run.py').")
    parser.add_argument("--justification", required=True, help="A detailed justification for why this change is necessary.")
    parser.add_argument("--proposed-changes", required=True, help="A description of the exact changes to be made.")
    
    args = parser.parse_args()
    
    os.makedirs(AMENDMENTS_DIR, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc)
    amendment_id = f"amendment_{timestamp.strftime('%Y%m%d%H%M%S')}.json"
    
    proposal = {
        "amendment_id": amendment_id,
        "timestamp_utc": timestamp.isoformat(),
        "status": "proposed",
        "target_file": args.target_file,
        "justification": args.justification,
        "proposed_changes": args.proposed_changes
    }
    
    file_path = os.path.join(AMENDMENTS_DIR, amendment_id)
    
    with open(file_path, 'w') as f:
        json.dump(proposal, f, indent=2)
        
    print(f"✅ Amendment proposal created successfully: {file_path}")

if __name__ == "__main__":
    main()