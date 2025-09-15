import os
import json
import base64
import argparse
import stat

# --- Helper functions for Fertilize Mode ---

def merge_json_file(path, new_content_bytes):
    """Merges a new JSON file with an existing one, overwriting keys."""
    try:
        new_data = json.loads(new_content_bytes.decode('utf-8'))
        if not isinstance(new_data, dict):
            print(f"  - Skipping merge for {path}: new content is not a dictionary.")
            return

        existing_data = {}
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"  - Warning: Existing file {path} is not valid JSON. Overwriting.")

        existing_data.update(new_data)

        with open(path, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"  Fertilized JSON: {path}")

    except Exception as e:
        print(f"  - ERROR merging JSON {path}: {e}. Skipping.")

def merge_log_file(path, new_content_bytes):
    """Appends unique lines from a new log file to an existing one."""
    try:
        new_lines = new_content_bytes.decode('utf-8').splitlines()

        existing_lines = set()
        if os.path.exists(path):
            with open(path, 'r') as f:
                existing_lines = set(line.strip() for line in f)

        with open(path, 'a') as f:
            for line in new_lines:
                if line.strip() and line.strip() not in existing_lines:
                    f.write(line + '\n')
        print(f"  Fertilized log: {path}")

    except Exception as e:
        print(f"  - ERROR merging log {path}: {e}. Skipping.")


def execute_protocol(seed_data):
    """Executes the steps defined in the germination_protocol."""
    print("--- Starting Reference Implementation of Germination Protocol ---")

    # Dynamic Fertilizer Detection
    is_fertilize_mode = os.path.exists("context/history.log")
    if is_fertilize_mode:
        print("[INFO] Existing Loop detected. Running in 'Fertilize' mode.")
    else:
        print("[INFO] No existing Loop detected. Running in 'Barren' mode.")

    protocol = seed_data.get("germination_protocol", [])
    file_map = seed_data.get("file_content_map", {})
    wisdom_files = {
        "analogies/registry.json": merge_json_file,
        "context/decisions.log": merge_log_file,
        "context/lessons.log": merge_log_file,
        "context/proven_workflows.json": merge_json_file
    }

    for step in protocol:
        action = step.get("action")
        path = step.get("path")

        try:
            if action == "log_message":
                print(f"[INFO] {step.get('message')}")

            elif action == "create_directory":
                if not os.path.exists(path):
                    os.makedirs(path)
                    print(f"  Created directory: {path}")
                else:
                    print(f"  Directory exists, skipping: {path}")

            elif action == "create_file":
                content_b64 = file_map.get(path)
                if content_b64 is None:
                    print(f"[ERROR] Content for '{path}' not found in file_content_map. Skipping.")
                    continue

                content_bytes = base64.b64decode(content_b64)

                # Ensure parent directory exists
                parent_dir = os.path.dirname(path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)

                # FERTILIZER LOGIC
                if is_fertilize_mode and os.path.exists(path):
                    if path in wisdom_files:
                        merge_func = wisdom_files[path]
                        merge_func(path, content_bytes)
                    else:
                        print(f"  File exists, skipping overwrite in fertilize mode: {path}")
                else:
                    # BARREN MODE or file doesn't exist
                    with open(path, 'wb') as f:
                        f.write(content_bytes)
                    print(f"  Created file: {path}")

            elif action == "make_executable":
                if os.path.exists(path):
                    st = os.stat(path)
                    os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                    print(f"  Made executable: {path}")
                else:
                    print(f"  [WARNING] Cannot make executable, file not found: {path}")

            elif action == "emergency_fallback":
                print("[INFO] Reached end of standard protocol.")
                pass

            else:
                print(f"[WARNING] Unknown action type '{action}' found in protocol. Skipping.")

        except Exception as e:
            print(f"[ERROR] Failed during action '{action}' on path '{path or 'N/A'}': {e}")

    print("--- Germination Protocol Execution Complete ---")


def main():
    """Main function to parse arguments and run the germination."""
    parser = argparse.ArgumentParser(description="Germinates a new Strange Loop from a genesis_seed.json file.")
    parser.add_argument(
        "--seed_file",
        required=True,
        help="Path to the genesis_seed.json file."
    )
    args = parser.parse_args()

    if not os.path.exists(args.seed_file):
        print(f"[FATAL] Seed file not found at: {args.seed_file}")
        return

    try:
        with open(args.seed_file, 'r') as f:
            seed_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FATAL] Could not parse seed file. Invalid JSON: {e}")
        return
    except Exception as e:
        print(f"[FATAL] Could not read seed file: {e}")
        return

    execute_protocol(seed_data)

if __name__ == "__main__":
    main()
