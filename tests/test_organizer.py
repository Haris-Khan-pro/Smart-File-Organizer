
import os
import tempfile
import unittest

from app.core.organizer import (
    organize,
    undo_organization,
)


class TestOrganizer(unittest.TestCase):

    def test_organize_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            source_file = os.path.join(
                temp_dir,
                "photo.jpg"
            )

            with open(source_file, "wb") as file:
                file.write(b"test image")

            files = [
                {
                    "name": "photo.jpg",
                    "path": source_file,
                    "extension": ".jpg",
                    "size": os.path.getsize(source_file),
                    "category": "Images",
                }
            ]

            result = organize(
                temp_dir,
                files
            )

            self.assertEqual(
                len(result["moved"]),
                1
            )

            self.assertEqual(
                len(result["errors"]),
                0
            )

            destination = os.path.join(
                temp_dir,
                "Images",
                "photo.jpg"
            )

            self.assertFalse(
                os.path.exists(source_file)
            )

            self.assertTrue(
                os.path.exists(destination)
            )

            self.assertEqual(
                result["moved"][0]["source"],
                source_file
            )

            self.assertEqual(
                result["moved"][0]["destination"],
                destination
            )

    def test_undo_organization(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            source_file = os.path.join(
                temp_dir,
                "document.txt"
            )

            with open(source_file, "wb") as file:
                file.write(b"test document")

            files = [
                {
                    "name": "document.txt",
                    "path": source_file,
                    "extension": ".txt",
                    "size": os.path.getsize(source_file),
                    "category": "Documents",
                }
            ]

            organize_result = organize(
                temp_dir,
                files
            )

            moved_files = organize_result["moved"]

            self.assertEqual(
                len(moved_files),
                1
            )

            undo_result = undo_organization(
                moved_files
            )

            self.assertEqual(
                len(undo_result["restored"]),
                1
            )

            self.assertEqual(
                len(undo_result["errors"]),
                0
            )

            self.assertTrue(
                os.path.exists(source_file)
            )

            destination = moved_files[0]["destination"]

            self.assertFalse(
                os.path.exists(destination)
            )

    def test_duplicate_filename_is_renamed(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            images_folder = os.path.join(
                temp_dir,
                "Images"
            )

            os.makedirs(
                images_folder
            )

            existing_file = os.path.join(
                images_folder,
                "photo.jpg"
            )

            with open(existing_file, "wb") as file:
                file.write(b"existing")

            source_file = os.path.join(
                temp_dir,
                "photo.jpg"
            )

            with open(source_file, "wb") as file:
                file.write(b"new")

            files = [
                {
                    "name": "photo.jpg",
                    "path": source_file,
                    "extension": ".jpg",
                    "size": os.path.getsize(source_file),
                    "category": "Images",
                }
            ]

            result = organize(
                temp_dir,
                files
            )

            self.assertEqual(
                len(result["moved"]),
                1
            )

            destination = result["moved"][0]["destination"]

            self.assertTrue(
                os.path.exists(destination)
            )

            self.assertEqual(
                os.path.basename(destination),
                "photo_1.jpg"
            )

            self.assertTrue(
                os.path.exists(existing_file)
            )

    def test_organize_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            missing_file = os.path.join(
                temp_dir,
                "missing.txt"
            )

            files = [
                {
                    "name": "missing.txt",
                    "path": missing_file,
                    "extension": ".txt",
                    "size": 100,
                    "category": "Documents",
                }
            ]

            result = organize(
                temp_dir,
                files
            )

            self.assertEqual(
                len(result["moved"]),
                0
            )

            self.assertEqual(
                len(result["errors"]),
                1
            )

    def test_organize_missing_source_reports_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = os.path.join(
                temp_dir,
                "missing.txt"
            )

            files = [
                {
                    "name": "missing.txt",
                    "path": missing_file,
                    "extension": ".txt",
                    "size": 12,
                    "category": "Documents",
                }
            ]

            result = organize(
                temp_dir,
                files
            )

            self.assertEqual(
                len(result["moved"]),
                0
            )

            self.assertEqual(
                len(result["errors"]),
                1
            )

    def test_organize_partial_failure_keeps_successful_moves(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_file = os.path.join(temp_dir, "keep.txt")
            missing_file = os.path.join(temp_dir, "missing.txt")

            with open(existing_file, "wb") as file:
                file.write(b"keep me")

            files = [
                {
                    "name": "keep.txt",
                    "path": existing_file,
                    "extension": ".txt",
                    "size": 7,
                    "category": "Documents",
                },
                {
                    "name": "missing.txt",
                    "path": missing_file,
                    "extension": ".txt",
                    "size": 12,
                    "category": "Documents",
                }
            ]

            result = organize(temp_dir, files)

            self.assertEqual(len(result["moved"]), 1)
            self.assertEqual(len(result["errors"]), 1)
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "Documents", "keep.txt")))

    def test_undo_repeated_attempt_reports_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = os.path.join(temp_dir, "repeat.txt")

            with open(source_file, "wb") as file:
                file.write(b"repeat")

            organize_result = organize(temp_dir, [{
                "name": "repeat.txt",
                "path": source_file,
                "extension": ".txt",
                "size": 6,
                "category": "Documents",
            }])

            first_undo = undo_organization(organize_result["moved"])
            self.assertEqual(len(first_undo["restored"]), 1)
            self.assertEqual(len(first_undo["errors"]), 0)

            second_undo = undo_organization(organize_result["moved"])
            self.assertEqual(len(second_undo["restored"]), 0)
            self.assertEqual(len(second_undo["errors"]), 1)

    def test_undo_conflict_with_existing_source_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = os.path.join(temp_dir, "existing.txt")
            destination = os.path.join(temp_dir, "Documents", "existing.txt")

            os.makedirs(os.path.dirname(destination), exist_ok=True)

            with open(source, "wb") as file:
                file.write(b"original")

            with open(destination, "wb") as file:
                file.write(b"moved")

            result = undo_organization([{
                "name": "existing.txt",
                "source": source,
                "destination": destination,
            }])

            self.assertEqual(len(result["restored"]), 0)
            self.assertEqual(len(result["errors"]), 1)

    def test_undo_with_invalid_history_record(self):
        result = undo_organization("not-a-list")

        self.assertEqual(result["restored"], [])
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Operation history is invalid", result["errors"][0]["error"])

    def test_undo_missing_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            source = os.path.join(
                temp_dir,
                "original.txt"
            )

            destination = os.path.join(
                temp_dir,
                "Documents",
                "original.txt"
            )

            moved_files = [
                {
                    "name": "original.txt",
                    "source": source,
                    "destination": destination,
                }
            ]

            result = undo_organization(
                moved_files
            )

            self.assertEqual(
                len(result["restored"]),
                0
            )

            self.assertEqual(
                len(result["errors"]),
                1
            )


if __name__ == "__main__":
    unittest.main()
