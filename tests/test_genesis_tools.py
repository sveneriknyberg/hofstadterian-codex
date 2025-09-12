import unittest
import os
import json
import subprocess
import tempfile
import shutil
import base64
import stat

# This assumes the test is run from the root of the repository
SEED_FILE_PATH = "artifacts/genesis_seed.json"
CREATE_SCRIPT_PATH = "scripts/create_seed.py"
GERMINATE_SCRIPT_PATH = "scripts/germinate.py"

class TestGenesisAndGermination(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Ensure the genesis_seed.json exists before running tests.
        If not, create it. This makes the test suite runnable on its own.
        """
        if not os.path.exists(SEED_FILE_PATH):
            print("Seed file not found. Running create_seed.py to generate it...")
            result = subprocess.run(["python3", CREATE_SCRIPT_PATH], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create seed file for testing:\n{result.stderr}")
            print("Seed file created successfully.")

    def test_1_seed_file_validation(self):
        """
        Tests that the genesis_seed.json file is valid and contains key elements.
        """
        print("\n--- Running Test 1: Seed File Validation ---")
        self.assertTrue(os.path.exists(SEED_FILE_PATH))

        with open(SEED_FILE_PATH, 'r') as f:
            data = json.load(f)

        # Check for top-level keys
        self.assertIn("metadata", data)
        self.assertIn("germination_protocol", data)
        self.assertIn("file_content_map", data)

        # Check for a known file and its content
        self.assertIn("AGENTS.md", data["file_content_map"])
        with open("AGENTS.md", "rb") as f_orig:
            original_content = f_orig.read()

        decoded_content = base64.b64decode(data["file_content_map"]["AGENTS.md"])
        self.assertEqual(original_content, decoded_content)
        print("Seed file structure and content are valid.")

    def test_2_germination_process(self):
        """
        Tests the end-to-end germination process in a temporary directory.
        """
        print("\n--- Running Test 2: Germination Process ---")
        with tempfile.TemporaryDirectory() as tmpdir:
            seed_file_abs_path = os.path.abspath(SEED_FILE_PATH)
            germinate_script_abs_path = os.path.abspath(GERMINATE_SCRIPT_PATH)

            # Run germinate.py in the temporary directory
            result = subprocess.run(
                ["python3", germinate_script_abs_path, "--seed_file", seed_file_abs_path],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            # Check for successful execution
            self.assertEqual(result.returncode, 0, f"germinate.py failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

            # Verify the file structure in the temporary directory
            # 1. Check for a key directory
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, "scripts")))
            # 2. Check for a key file
            germinated_agents_md = os.path.join(tmpdir, "AGENTS.md")
            self.assertTrue(os.path.isfile(germinated_agents_md))
            # 3. Check file content
            with open(germinated_agents_md, 'r') as f:
                created_content = f.read()
            with open("AGENTS.md", 'r') as f:
                original_content = f.read()
            self.assertEqual(created_content, original_content)
            # 4. Check for executable permission
            bootstrap_script = os.path.join(tmpdir, "scripts/agent_bootstrap.sh")
            self.assertTrue(os.path.exists(bootstrap_script))
            self.assertTrue(os.access(bootstrap_script, os.X_OK))
            print("Germination process created the correct file structure and permissions.")


if __name__ == '__main__':
    unittest.main()
