
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
                0
            )

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
