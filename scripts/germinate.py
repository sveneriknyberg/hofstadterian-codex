import os
import json
import base64
import argparse
import stat

def execute_protocol(seed_data):
    """Executes the steps defined in the germination_protocol."""

    print("--- Starting Reference Implementation of Germination Protocol ---")

    protocol = seed_data.get("germination_protocol", [])
    file_map = seed_data.get("file_content_map", {})

    for step in protocol:
        action = step.get("action")

        try:
            if action == "log_message":
                print(f"[INFO] {step.get('message')}")

            elif action == "create_directory":
                path = step.get("path")
                if not os.path.exists(path):
                    os.makedirs(path)
                    print(f"  Created directory: {path}")
                else:
                    print(f"  Directory exists, skipping: {path}")

            elif action == "create_file":
                path = step.get("path")
                content_b64 = file_map.get(path)
                if content_b64 is None:
                    print(f"[ERROR] Content for '{path}' not found in file_content_map. Skipping.")
                    continue

                # Ensure parent directory exists, just in case protocol order is not perfect
                parent_dir = os.path.dirname(path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)

                content_bytes = base64.b64decode(content_b64)
                with open(path, 'wb') as f:
                    f.write(content_bytes)
                print(f"  Created file: {path}")

            elif action == "make_executable":
                path = step.get("path")
                # Add execute permissions for user, group, and others
                st = os.stat(path)
                os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                print(f"  Made executable: {path}")

            elif action == "emergency_fallback":
                # The reference implementation does not execute the fallback.
                print("[INFO] Reached end of standard protocol.")
                pass

            else:
                print(f"[WARNING] Unknown action type '{action}' found in protocol. Skipping.")

        except Exception as e:
            print(f"[ERROR] Failed during action '{action}' on path '{step.get('path', 'N/A')}': {e}")

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
