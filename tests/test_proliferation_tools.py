import os
import sys
import json
import pytest

# Add the 'scripts' directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts import export_wisdom, import_wisdom

@pytest.fixture
def setup_wisdom_test_env(tmp_path):
    """Sets up a temporary environment for wisdom import/export testing."""
    project_root = tmp_path
    # Create source directories
    (project_root / "analogies").mkdir()
    (project_root / "context").mkdir()

    # Change CWD to the temp root
    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield project_root
    os.chdir(original_cwd)

def test_export_wisdom(setup_wisdom_test_env):
    """Tests the successful creation of a wisdom packet."""
    project_root = setup_wisdom_test_env

    # 1. Create mock source files
    (project_root / "analogies" / "registry.json").write_text('{"analogy1": {"rationale": "r1"}}')
    (project_root / "context" / "lessons.log").write_text("lesson1\nlesson2")
    (project_root / "context" / "decisions.log").write_text("decision1")
    (project_root / "context" / "proven_workflows.json").write_text('[{"name": "wf1"}]')

    # 2. Run the export script
    export_wisdom.main()

    # 3. Assert the output
    packet_path = project_root / "wisdom_packet.json"
    assert packet_path.exists()
    with open(packet_path, 'r') as f:
        packet_data = json.load(f)

    assert "analogies" in packet_data
    assert packet_data["analogies"]["analogy1"]["rationale"] == "r1"
    assert "lessons" in packet_data
    assert "lesson1" in packet_data["lessons"]
    assert "decisions" in packet_data
    assert "decision1" in packet_data["decisions"]
    assert "workflows" in packet_data
    assert packet_data["workflows"][0]["name"] == "wf1"

def test_import_wisdom(setup_wisdom_test_env):
    """Tests the successful import and merging of a wisdom packet."""
    project_root = setup_wisdom_test_env

    # 1. Create a mock wisdom packet
    packet_data = {
        "analogies": {"new_analogy": {"rationale": "new_r"}},
        "lessons": ["new_lesson", "lesson1"], # "lesson1" is a duplicate
        "decisions": ["new_decision"],
        "workflows": [{"success_timestamp": "T01", "name": "new_wf"}]
    }
    (project_root / "wisdom_packet.json").write_text(json.dumps(packet_data))

    # 2. Create mock local files that already have some content
    (project_root / "analogies" / "registry.json").write_text('{"local_analogy": {}}')
    (project_root / "context" / "lessons.log").write_text("lesson1\n")
    (project_root / "context" / "decisions.log").write_text("") # empty log
    (project_root / "context" / "proven_workflows.json").write_text('[]')

    # 3. Run the import script
    import_wisdom.main()

    # 4. Assert the merged results
    # Analogies (dict merge)
    analogies_path = project_root / "analogies" / "registry.json"
    with open(analogies_path, 'r') as f:
        analogies_data = json.load(f)
    assert "local_analogy" in analogies_data
    assert "new_analogy" in analogies_data

    # Lessons (append unique)
    lessons_path = project_root / "context" / "lessons.log"
    with open(lessons_path, 'r') as f:
        lessons_data = f.read()
    assert "lesson1" in lessons_data
    assert "new_lesson" in lessons_data
    assert lessons_data.count("lesson1") == 1 # Check for no duplicates

    # Workflows (append unique)
    workflows_path = project_root / "context" / "proven_workflows.json"
    with open(workflows_path, 'r') as f:
        workflows_data = json.load(f)
    assert len(workflows_data) == 1
    assert workflows_data[0]["name"] == "new_wf"

    # 5. Assert the packet was renamed
    assert not (project_root / "wisdom_packet.json").exists()
    assert (project_root / "wisdom_packet.imported").exists()
