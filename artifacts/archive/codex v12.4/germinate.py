import os
import json
import base64
import argparse
import stat
import urllib.request
import gzip

def execute_protocol(seed_data):
    protocol = seed_data.get("germination_protocol", [])
    file_map = seed_data.get("file_content_map", {})
    metadata = seed_data.get("metadata", {})
    compression_method = metadata.get("compression")

    for step in protocol:
        action = step.get("action")
        path = step.get("path")
        try:
            if action == "log_message":
                print(f"[INFO] {step.get('message')}")
            elif action == "create_directory":
                os.makedirs(path, exist_ok=True)
                print(f"  Created directory: {path}")
            elif action == "create_file":
                content_encoded = file_map.get(path)
                if content_encoded is None:
                    print(f"[ERROR] Content for '{path}' not found in file_content_map. Skipping.")
                    continue

                content_bytes = base64.b64decode(content_encoded)
                if compression_method == "gzip+base64":
                    content_bytes = gzip.decompress(content_bytes)

                with open(path, 'wb') as f:
                    f.write(content_bytes)
                print(f"  Created file: {path}")
            elif action == "fetch_file_from_url":
                url = step.get("url")
                urllib.request.urlretrieve(url, path)
                print(f"  Fetched file from {url}: {path}")
            elif action == "make_executable":
                st = os.stat(path)
                os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                print(f"  Made executable: {path}")
        except Exception as e:
            print(f"[ERROR] Failed during action '{action}' on path '{path or 'N/A'}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Germinates a New Loop from a Genesis Seed.")
    parser.add_argument("--seed_file", required=True, help="Path to the genesis_seed.json file.")
    args = parser.parse_args()

    if not os.path.exists(args.seed_file):
        print(f"[FATAL] Seed file not found at: {args.seed_file}")
        return

    with open(args.seed_file, 'r') as f:
        seed_data = json.load(f)

    execute_protocol(seed_data)

if __name__ == "__main__":
    main()
