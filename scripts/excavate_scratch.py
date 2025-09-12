import os
import re

# --- Constants ---
HANDOFF_DIR = "handoffs"
SCRATCH_DIR = "scratch"
UNRESOLVED_ISSUES_HEADER = "## 6. Unresolved Issues & Next Steps"
# Simple stop words to improve keyword quality
STOP_WORDS = {'a', 'an', 'the', 'is', 'to', 'be', 'from', 'it', 'in', 'and', 'or', 'as', 'for', 'of'}

# --- Helper Functions ---

def extract_keywords(text):
    """Extracts simple, meaningful keywords from a line of text."""
    # Remove markdown, punctuation, and make lowercase
    text = re.sub(r'[`*-]', '', text).lower()
    words = re.findall(r'\b\w+\b', text)
    # Return non-stop words that are longer than 2 chars
    return {word for word in words if word not in STOP_WORDS and len(word) > 2}

def get_unresolved_issues(handoff_path):
    """Parses a handoff file and returns a list of unresolved issues."""
    issues = []
    try:
        with open(handoff_path, 'r') as f:
            lines = f.readlines()

        in_issues_section = False
        for line in lines:
            if line.strip() == UNRESOLVED_ISSUES_HEADER:
                in_issues_section = True
                continue

            if in_issues_section:
                # Stop if we hit the next section
                if line.startswith('## '):
                    break
                # Capture bullet points
                if line.strip().startswith('- '):
                    issues.append(line.strip('- ').strip())
    except IOError:
        pass # Ignore files that can't be read
    return issues

# --- Main Logic ---

def main():
    print("--- Starting Archaeological Excavation ---")

    # 1. Gather all unresolved issues from all handoffs
    all_issues = []
    if os.path.isdir(HANDOFF_DIR):
        for filename in sorted(os.listdir(HANDOFF_DIR)):
            if filename.endswith(".md"):
                path = os.path.join(HANDOFF_DIR, filename)
                all_issues.extend(get_unresolved_issues(path))

    if not all_issues:
        print("No unresolved issues found in any handoffs.")
        print("--- Excavation Complete ---")
        return

    # 2. Gather all scratch files
    scratch_files = []
    if os.path.isdir(SCRATCH_DIR):
        for filename in os.listdir(SCRATCH_DIR):
            path = os.path.join(SCRATCH_DIR, filename)
            if os.path.isfile(path):
                scratch_files.append(path)

    if not scratch_files:
        print("No files found in the scratch directory to analyze.")
        print("--- Excavation Complete ---")
        return

    print(f"Found {len(all_issues)} unresolved issue(s) and {len(scratch_files)} scratch file(s).")
    print("Searching for correlations...")

    # 3. Match issues to scratch files
    matches_found = 0
    for issue in all_issues:
        issue_keywords = extract_keywords(issue)
        if not issue_keywords:
            continue

        for scratch_file in scratch_files:
            try:
                with open(scratch_file, 'r') as f:
                    content = f.read().lower()

                filename_lower = os.path.basename(scratch_file).lower()

                # Check for any keyword match in filename or content
                matched_keywords = {kw for kw in issue_keywords if kw in filename_lower or kw in content}

                if matched_keywords:
                    matches_found += 1
                    print("\n[!] Potential Match Found!")
                    print(f"  - Unresolved Issue: '{issue}'")
                    print(f"  - Scratch File:     '{scratch_file}'")
                    print(f"  - Matched Keywords: {', '.join(sorted(list(matched_keywords)))}")

            except (IOError, UnicodeDecodeError):
                # Ignore binary files or files with reading errors
                continue

    if matches_found == 0:
        print("No correlations found between unresolved issues and scratch files.")

    print("--- Excavation Complete ---")

if __name__ == "__main__":
    main()
