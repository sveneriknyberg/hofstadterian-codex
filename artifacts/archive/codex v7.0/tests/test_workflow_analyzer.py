import os
import sys
import json
import pytest

# Add the 'scripts' directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import workflow_analyzer

@pytest.fixture
def setup_workflow_test_env(tmp_path):
    """Sets up a temporary environment for workflow analysis testing."""
    project_root = tmp_path
    context_dir = project_root / "context"
    context_dir.mkdir()

    # Create an empty proven_workflows.json
    (context_dir / "proven_workflows.json").write_text("[]")

    # Change CWD to the temp root
    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield project_root
    os.chdir(original_cwd)

def test_discover_test_fix_workflow(setup_workflow_test_env):
    """
    Tests if a standard 'test fix' workflow is correctly discovered and logged.
    Pattern: test fails -> code is changed -> test passes
    """
    project_root = setup_workflow_test_env

    # 1. Create a mock session history with the pattern
    session_history_path = project_root / ".session_history.json"
    history_data = [
        # An irrelevant command
        {"tool_name": "ls", "command": "ls", "status": "success", "timestamp": "T01"},
        # The test failure
        {"tool_name": "run_in_bash_session", "command": "pytest", "status": "error", "timestamp": "T02"},
        # The fix
        {"tool_name": "replace_with_git_merge_diff", "tool_args": ["src/main.py"], "status": "success", "timestamp": "T03"},
        # The test success
        {"tool_name": "run_in_bash_session", "command": "pytest", "status": "success", "timestamp": "T04"},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    # 2. Run the analyzer
    workflow_analyzer.main()

    # 3. Read the results and assert
    proven_workflows_path = project_root / "context" / "proven_workflows.json"
    with open(proven_workflows_path, 'r') as f:
        workflows = json.load(f)

    assert len(workflows) == 1
    discovered_workflow = workflows[0]
    assert discovered_workflow["name"] == "Workflow that fixed tests related to: src/main.py"
    assert discovered_workflow["success_timestamp"] == "T04"
    assert len(discovered_workflow["sequence"]) == 1
    assert discovered_workflow["sequence"][0]["tool_name"] == "replace_with_git_merge_diff"
    assert discovered_workflow["sequence"][0]["tool_args"][0] == "src/main.py"

def test_no_workflow_if_no_intervening_action(setup_workflow_test_env):
    """
    Tests that no workflow is logged if the fix is empty or just observation.
    """
    project_root = setup_workflow_test_env

    session_history_path = project_root / ".session_history.json"
    history_data = [
        {"tool_name": "run_in_bash_session", "command": "pytest", "status": "error", "timestamp": "T01"},
        {"tool_name": "read_file", "tool_args": ["src/main.py"], "status": "success", "timestamp": "T02"}, # No edit
        {"tool_name": "run_in_bash_session", "command": "pytest", "status": "success", "timestamp": "T03"},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    workflow_analyzer.main()

    proven_workflows_path = project_root / "context" / "proven_workflows.json"
    with open(proven_workflows_path, 'r') as f:
        workflows = json.load(f)

    assert len(workflows) == 0

def test_no_workflow_if_no_prior_failure(setup_workflow_test_env):
    """
    Tests that no workflow is logged for a test success if there was no
    preceding failure in the recent history.
    """
    project_root = setup_workflow_test_env

    session_history_path = project_root / ".session_history.json"
    history_data = [
        {"tool_name": "replace_with_git_merge_diff", "tool_args": ["src/main.py"], "status": "success", "timestamp": "T01"},
        {"tool_name": "run_in_bash_session", "command": "pytest", "status": "success", "timestamp": "T02"},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    workflow_analyzer.main()

    proven_workflows_path = project_root / "context" / "proven_workflows.json"
    with open(proven_workflows_path, 'r') as f:
        workflows = json.load(f)

    assert len(workflows) == 0
