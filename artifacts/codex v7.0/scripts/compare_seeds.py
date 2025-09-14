import json
import base64
import os
import difflib
import argparse

def load_seed(filepath):
    """Loads a seed file and returns its file content map."""
    if not os.path.exists(filepath):
        print(f"ERROR: Seed file not found at {filepath}")
        return None
    with open(filepath, 'r') as f:
        seed_data = json.load(f)
    return seed_data.get("file_content_map", {})

def main():
    """Compares two seed files and prints a report of the differences."""
    parser = argparse.ArgumentParser(
        description="Compares two genesis_seed.json files and reports the differences in their file maps."
    )
    parser.add_argument("base_seed_path", help="Path to the base (original) seed file.")
    parser.add_argument("new_seed_path", help="Path to the new seed file to compare against the base.")
    args = parser.parse_args()

    print("--- Comparing Seed Files ---")
    print(f"Base: {args.base_seed_path}")
    print(f"New:  {args.new_seed_path}\n")

    base_map = load_seed(args.base_seed_path)
    new_map = load_seed(args.new_seed_path)

    if base_map is None or new_map is None:
        return

    base_files = set(base_map.keys())
    new_files = set(new_map.keys())

    added_files = new_files - base_files
    removed_files = base_files - new_files
    common_files = new_files.intersection(base_files)

    modified_files = []
    for f in common_files:
        if base_map[f] != new_map[f]:
            modified_files.append(f)

    if not added_files and not removed_files and not modified_files:
        print("Result: No divergence found. The file content maps are identical.")
        return

    if added_files:
        print("--- Added Files ---")
        for f in sorted(list(added_files)):
            print(f"- {f}")
        print()

    if removed_files:
        print("--- Removed Files ---")
        for f in sorted(list(removed_files)):
            print(f"- {f}")
        print()

    if modified_files:
        print("--- Modified Files ---")
        for f in sorted(modified_files):
            print(f"--- Diff for: {f} ---")
            try:
                base_content = base64.b64decode(base_map[f]).decode('utf-8').splitlines()
                new_content = base64.b64decode(new_map[f]).decode('utf-8').splitlines()

                diff = difflib.unified_diff(
                    base_content, new_content,
                    fromfile=f'a/{f}', tofile=f'b/{f}',
                    lineterm=''
                )
                for line in diff:
                    print(line)
                print("-" * 20)
                print()

            except Exception as e:
                print(f"Could not generate diff for {f}: {e}")

if __name__ == "__main__":
    main()
