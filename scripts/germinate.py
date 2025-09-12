import os
import json
import base64
import stat
import sys

# --- Main Logic ---

def main():
    """
    Reads a genesis_seed.json file and builds a complete Loop infrastructure
    in the current directory from its contents.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 germinate.py <path_to_genesis_seed.json>")
        sys.exit(1)

    seed_file_path = sys.argv[1]

    if not os.path.exists(seed_file_path):
        print(f"Error: Seed file not found at {seed_file_path}")
        sys.exit(1)

    print(f"Germinating new Loop from seed: {seed_file_path}")

    try:
        with open(seed_file_path, 'r') as f:
            seed_data = json.load(f)
    except Exception as e:
        print(f"Error reading or parsing seed file: {e}")
        sys.exit(1)

    # 1. Create directory structure
    print("\nCreating directories...")
    for dir_path in seed_data.get("directories", []):
        if dir_path: # Avoid trying to create the root ""
            os.makedirs(dir_path, exist_ok=True)
            print(f"  - Created {dir_path}/")

    # 2. Create files from base64 content
    print("\nCreating files...")
    for file_info in seed_data.get("files", []):
        file_path = file_info.get("path")
        content_b64 = file_info.get("content_b64")
        is_executable = file_info.get("executable", False)

        if not file_path or content_b64 is None:
            print(f"Warning: Skipping invalid file entry: {file_info}")
            continue

        try:
            content_bytes = base64.b64decode(content_b64)
            with open(file_path, 'wb') as f:
                f.write(content_bytes)
            print(f"  - Created {file_path}")

            # Set executable permissions if required
            if is_executable:
                # Get current permissions and add execute bit for owner, group, and others
                current_stats = os.stat(file_path)
                os.chmod(file_path, current_stats.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                print(f"    - Made executable")

        except Exception as e:
            print(f"Error creating file {file_path}: {e}")

    print("\nGermination complete. The Loop is ready.")
    print("Run 'bash scripts/agent_bootstrap.sh' to initialize the first session.")


if __name__ == "__main__":
    main()
