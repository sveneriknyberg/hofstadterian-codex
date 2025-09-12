import os
import sys
import json
import pytest

# Add the 'scripts' directory to the python path so we can import our script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import meta_cognitive_check

@pytest.fixture
def setup_test_environment(tmp_path):
    """
    Creates a temporary directory structure that mimics the project root,
    including dummy trigger and analogy files for the test.
    """
    project_root = tmp_path
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir()
    analogies_dir = project_root / "analogies"
    analogies_dir.mkdir()

    # Create a dummy triggers file with an analogy link and contextual messages
    triggers_content = """
patterns:
  - name: "Analysis Paralysis"
    type: "sequence"
    tools: ["read_file", "ls"]
    threshold: 2
    analogy_id: "environment_as_unreliable_narrator"
    message: "You seem to be observing a lot."
  - name: "Tool Fixation"
    type: "repetition"
    threshold: 3
    message: "The tool '{tool_name}' has failed {count} times." # Default message
    contextual_messages:
      "pytest": "Your test suite ('pytest') appears to be failing."
      "pip install": "Dependency installation with 'pip install' appears to be failing."
"""
    (scripts_dir / "meta_triggers.yaml").write_text(triggers_content)

    # Create a dummy analogies registry
    analogies_content = {"environment_as_unreliable_narrator": {"rationale": "The environment can be tricky."}}
    (analogies_dir / "registry.json").write_text(json.dumps(analogies_content))

    return project_root

def test_analysis_paralysis_with_analogy(setup_test_environment, capsys):
    project_root = setup_test_environment
    session_history_path = project_root / ".session_history.json"
    history_data = [{"tool_name": "ls"}, {"tool_name": "read_file"}]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        meta_cognitive_check.main()
    finally:
        os.chdir(original_cwd)

    captured = capsys.readouterr()
    assert "You seem to be observing a lot." in captured.out
    assert "[Suggested Analogy]: environment_as_unreliable_narrator" in captured.out
    assert "The environment can be tricky." in captured.out

def test_tool_fixation_with_contextual_message(setup_test_environment, capsys):
    """
    Tests if the 'Tool Fixation' trigger correctly uses the specific
    contextual message instead of the default one.
    """
    project_root = setup_test_environment
    session_history_path = project_root / ".session_history.json"

    # Simulate 3 failures of the same command
    error_output = "pytest failed: 1 test failed."
    history_data = [
        {"tool_name": "run_in_bash_session", "status": "error", "command": "python -m pytest", "output": error_output},
        {"tool_name": "run_in_bash_session", "status": "error", "command": "python -m pytest", "output": error_output},
        {"tool_name": "run_in_bash_session", "status": "error", "command": "python -m pytest", "output": error_output},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        meta_cognitive_check.main()
    finally:
        os.chdir(original_cwd)

    captured = capsys.readouterr()

    # Assert that the specific message for 'pytest' is present
    assert "Your test suite ('pytest') appears to be failing." in captured.out

    # Assert that the default, generic message is NOT present
    assert "The tool 'run_in_bash_session' has failed 3 times." not in captured.out

def test_tool_fixation_uses_default_message_if_no_context(setup_test_environment, capsys):
    """
    Tests if the 'Tool Fixation' trigger falls back to the default message
    when no contextual keyword matches.
    """
    project_root = setup_test_environment
    session_history_path = project_root / ".session_history.json"

    error_output = "some other command failed"
    history_data = [
        {"tool_name": "run_in_bash_session", "status": "error", "command": "some_other_command", "output": error_output},
        {"tool_name": "run_in_bash_session", "status": "error", "command": "some_other_command", "output": error_output},
        {"tool_name": "run_in_bash_session", "status": "error", "command": "some_other_command", "output": error_output},
    ]
    with open(session_history_path, 'w') as f:
        json.dump(history_data, f)

    original_cwd = os.getcwd()
    os.chdir(project_root)
    try:
        meta_cognitive_check.main()
    finally:
        os.chdir(original_cwd)

    captured = capsys.readouterr()

    # Assert that it falls back to the default message
    assert "The tool 'run_in_bash_session' has failed 3 times." in captured.out

    # Assert that the specific message is NOT present
    assert "Your test suite ('pytest') appears to be failing." not in captured.out
