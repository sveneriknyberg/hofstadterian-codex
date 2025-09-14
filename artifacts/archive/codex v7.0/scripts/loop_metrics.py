import os
import json

# --- Constants ---
# Define paths relative to the project root.
# The script assumes it is run from the project root.
HANDOFFS_DIR = "handoffs"
CONTEXT_DIR = "context"
ANALOGIES_DIR = "analogies"

DECISIONS_LOG = os.path.join(CONTEXT_DIR, "decisions.log")
LESSONS_LOG = os.path.join(CONTEXT_DIR, "lessons.log")
ANALOGY_REGISTRY = os.path.join(ANALOGIES_DIR, "registry.json")

RECURSIVE_IMPROVEMENT_THRESHOLD = 10

def count_files_in_dir(directory):
    """Counts the number of files in a given directory."""
    if not os.path.isdir(directory):
        return 0
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

def count_lines_in_file(filepath):
    """Counts the number of non-empty lines in a file."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r') as f:
            return len([line for line in f if line.strip()])
    except IOError:
        return 0

def count_keys_in_json(filepath):
    """Counts the number of top-level keys in a JSON file."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return len(data.keys())
    except (json.JSONDecodeError, IOError):
        return 0

def main():
    """Main function to calculate and display loop metrics."""
    print("--- Calculating Strange Loop Metrics ---")

    # Calculate metrics
    num_handoffs = count_files_in_dir(HANDOFFS_DIR)
    num_decisions = count_lines_in_file(DECISIONS_LOG)
    num_lessons = count_lines_in_file(LESSONS_LOG)
    num_analogies = count_keys_in_json(ANALOGY_REGISTRY)

    # Display metrics
    print(f"\n📈 Current Loop State:")
    print(f"  - Total Handoffs:     {num_handoffs}")
    print(f"  - Total Decisions:    {num_decisions}")
    print(f"  - Total Lessons:      {num_lessons}")
    print(f"  - Total Analogies:    {num_analogies}")

    # Check for Recursive Improvement
    if num_handoffs > 0 and num_handoffs % RECURSIVE_IMPROVEMENT_THRESHOLD == 0:
        print("\n" + "="*40)
        print("  !!! RECURSIVE IMPROVEMENT ALERT !!!")
        print(f"  The Loop has reached {num_handoffs} handoffs.")
        print("  It is time to review the Loop's evolution,")
        print("  celebrate successes, and identify areas for")
        print("  protocol improvement.")
        print("="*40)

    print("\n--- Metrics Calculation Complete ---")


if __name__ == "__main__":
    main()
