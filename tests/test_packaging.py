import tomllib
import unittest
from pathlib import Path


class TestPackagingMetadata(unittest.TestCase):

    def test_pyproject_includes_application_metadata_and_entry_point(self):
        project_root = Path(__file__).resolve().parents[1]
        pyproject_path = project_root / "pyproject.toml"

        self.assertTrue(pyproject_path.exists(), "pyproject.toml is required for packaging metadata")

        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        project = data["project"]
        self.assertEqual(project["name"], "smart-file-organizer")
        self.assertEqual(project["version"], "1.0.0")
        self.assertIn("smart-file-organizer", project["scripts"])


if __name__ == "__main__":
    unittest.main()
