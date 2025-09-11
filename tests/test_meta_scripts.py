import os
import sys
import json
import pytest

# Add the 'scripts' directory to the python path so we can import our script
# This allows the test runner to find the module.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the script we want to test
from scripts import meta_cognitive_check

@pytest.fixture
def setup_test_environment(tmp_path):
    """
    Creates a temporary directory structure that mimics the project root,
    including a dummy triggers file for the test.
    """
    project_root = tmp_path
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()

    # Create a dummy triggers file in the temp scripts dir.
    # This isolates the test from the actual triggers file.
    triggers_content = """
patterns:
  - name: "Analysis Paralysis"
    type: "sequence"
    description: "The agent appears to be stuck in a loop of observing without acting."
    tools: ["read_file", "ls", "grep"]
    threshold: 5
    message: |
      [!] Finding: You have used {count} read-only tools in a row ({tool_list}).
      - Am I gathering more information than I need?
"""
    (scripts_dir / "meta_triggers.yaml").write_text(triggers_content)

    return project_root

def test_analysis_paralysis_trigger(setup_test_environment, capsys):
    """
    Tests if the 'Analysis Paralysis' pattern is correctly detected by
    running the script's main function in a controlled environment.
    """
    project_root = setup_test_environment

    # 1. Create a dummy session history file in the temporary project root
    session_history_path = project_root / ".session_history.json"
    history_data = [
        {"tool_name": "ls", "status": "success"},
        {"tool_name": "read_file", "status": "success"},
        {"tool_name": "ls", "status": "success"},
        {"tool_name": "grep", "status": "success"},
        {"tool_name": "read_file", "status": "success"},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    # 2. Change CWD to the temporary project root so the script can find its files
    # using its os.getcwd() logic.
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        # 3. Run the main function of the script
        meta_cognitive_check.main()
    finally:
        # 4. Always change back to the original CWD, even if the test fails
        os.chdir(original_cwd)

    # 5. Capture the output and assert that the correct finding was reported
    captured = capsys.readouterr()
    assert "[!] Finding: You have used 5 read-only tools in a row" in captured.out
    assert "Am I gathering more information than I need?" in captured.out
