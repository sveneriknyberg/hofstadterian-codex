import unittest
import os
import json
import subprocess
import tempfile
import shutil
import base64
import stat
import glob

# This assumes the test is run from the root of the repository
CREATE_SCRIPT_PATH = "scripts/create_seed.py"
GERMINATE_SCRIPT_PATH = "scripts/germinate.py"

class TestGenesisAndGermination(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Ensure a default seed file exists before running tests.
        This makes the test suite runnable on its own.
        """
        # We run with the default name to have a predictable file for germination tests
        if not glob.glob("artifacts/genesis_seed-unnamed-loop-*.json"):
            print("Default seed file not found. Running create_seed.py to generate it...")
            result = subprocess.run(["python3", CREATE_SCRIPT_PATH], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create seed file for testing:\n{result.stderr}")
            print("Default seed file created successfully.")

        # Get the full path of the created seed for other tests to use
        cls.default_seed_path = glob.glob("artifacts/genesis_seed-unnamed-loop-*.json")[0]


    def test_1_seed_file_validation(self):
        """
        Tests that the genesis_seed.json file is valid and contains key elements.
        """
        print("\n--- Running Test 1: Seed File Validation ---")
        self.assertTrue(os.path.exists(self.default_seed_path))

        with open(self.default_seed_path, 'r') as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("germination_protocol", data)
        self.assertIn("file_content_map", data)
        self.assertIn("AGENTS.md", data["file_content_map"])

        with open("AGENTS.md", "rb") as f_orig:
            original_content = f_orig.read()
        decoded_content = base64.b64decode(data["file_content_map"]["AGENTS.md"])
        self.assertEqual(original_content, decoded_content)
        print("Seed file structure and content are valid.")

    def test_2_germination_barren_mode(self):
        """
        Tests the end-to-end germination process in a temporary (barren) directory.
        """
        print("\n--- Running Test 2: Germination in Barren Mode ---")
        with tempfile.TemporaryDirectory() as tmpdir:
            seed_file_abs_path = os.path.abspath(self.default_seed_path)
            germinate_script_abs_path = os.path.abspath(GERMINATE_SCRIPT_PATH)

            result = subprocess.run(
                ["python3", germinate_script_abs_path, "--seed_file", seed_file_abs_path],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0, f"germinate.py failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
            self.assertIn("Running in 'Barren' mode", result.stdout)

            germinated_agents_md = os.path.join(tmpdir, "AGENTS.md")
            self.assertTrue(os.path.isfile(germinated_agents_md))
            bootstrap_script = os.path.join(tmpdir, "scripts/agent_bootstrap.sh")
            self.assertTrue(os.path.exists(bootstrap_script))
            self.assertTrue(os.access(bootstrap_script, os.X_OK))
            print("Germination (Barren Mode) created the correct file structure and permissions.")

    def test_3_seed_creation_with_project_name(self):
        """
        Tests that create_seed.py generates a file with the correct dynamic name.
        """
        print("\n--- Running Test 3: Seed Creation with Project Name ---")
        project_name = "test-project"
        result = subprocess.run(
            ["python3", CREATE_SCRIPT_PATH, "--project_name", project_name],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, f"create_seed.py failed:\n{result.stderr}")

        # Find the created file
        created_files = glob.glob(f"artifacts/genesis_seed-{project_name}-*.json")
        self.assertEqual(len(created_files), 1, "Expected one seed file to be created for the test project.")

        # Clean up the created file
        os.remove(created_files[0])
        print(f"Successfully created and cleaned up named seed file: {created_files[0]}")

    def test_4_germination_fertilizer_mode(self):
        """
        Tests that germination correctly merges with an existing environment.
        """
        print("\n--- Running Test 4: Germination in Fertilizer Mode ---")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create a mock pre-existing environment
            context_dir = os.path.join(tmpdir, "context")
            os.makedirs(context_dir)

            original_lesson = "This is a pre-existing lesson."
            existing_lessons_path = os.path.join(context_dir, "lessons.log")
            with open(existing_lessons_path, 'w') as f:
                f.write(original_lesson + '\n')

            existing_script_path = os.path.join(tmpdir, "scripts")
            os.makedirs(existing_script_path)
            original_script_content = "#!/bin/bash\necho 'This is an old script that should not be overwritten.'"
            with open(os.path.join(existing_script_path, "agent_bootstrap.sh"), 'w') as f:
                f.write(original_script_content)

            # Also need the history log to trigger fertilize mode
            with open(os.path.join(context_dir, "history.log"), 'w') as f:
                f.write("Some old history.\n")

            # 2. Run germination
            seed_file_abs_path = os.path.abspath(self.default_seed_path)
            germinate_script_abs_path = os.path.abspath(GERMINATE_SCRIPT_PATH)
            result = subprocess.run(
                ["python3", germinate_script_abs_path, "--seed_file", seed_file_abs_path],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            # 3. Assertions
            self.assertEqual(result.returncode, 0, f"germinate.py (fertilize) failed:\n{result.stdout}\n{result.stderr}")
            self.assertIn("Running in 'Fertilize' mode", result.stdout)
            self.assertIn("Fertilized log: context/lessons.log", result.stdout)
            self.assertIn("File exists, skipping overwrite in fertilize mode: scripts/agent_bootstrap.sh", result.stdout)

            # Check that the lessons log was appended to, not overwritten
            with open(existing_lessons_path, 'r') as f:
                lessons_content = f.read()
            self.assertIn(original_lesson, lessons_content)
            self.assertIn('The environment is an "unreliable narrator."', lessons_content) # A known lesson from the seed

            # Check that the script was NOT overwritten
            with open(os.path.join(existing_script_path, "agent_bootstrap.sh"), 'r') as f:
                script_content = f.read()
            self.assertEqual(original_script_content, script_content)

            print("Germination (Fertilizer Mode) correctly merged wisdom and skipped overwriting existing files.")


if __name__ == '__main__':
    unittest.main()
