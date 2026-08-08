
import os
import tempfile
import unittest

from app.core.scanner import (
    get_category,
    calculate_file_hash,
    find_duplicates,
    scan,
)


class TestScanner(unittest.TestCase):

    def test_get_category(self):
        self.assertEqual(get_category(".jpg"), "Images")
        self.assertEqual(get_category(".pdf"), "Documents")
        self.assertEqual(get_category(".mp4"), "Videos")
        self.assertEqual(get_category(".mp3"), "Audio")
        self.assertEqual(get_category(".zip"), "Archives")
        self.assertEqual(get_category(".py"), "Code")
        self.assertEqual(get_category(".exe"), "Executables")
        self.assertEqual(get_category(".xyz"), "Other")

    def test_get_category_case_insensitive(self):
        self.assertEqual(get_category(".JPG"), "Images")
        self.assertEqual(get_category(".PDF"), "Documents")

    def test_calculate_file_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = os.path.join(
                temp_dir,
                "test.txt"
            )

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    b"Smart File Organizer"
                )

            file_hash = calculate_file_hash(
                file_path
            )

            self.assertIsNotNone(file_hash)
            self.assertEqual(
                len(file_hash),
                64
            )

    def test_find_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            file_1 = os.path.join(
                temp_dir,
                "file1.txt"
            )

            file_2 = os.path.join(
                temp_dir,
                "file2.txt"
            )

            with open(
                file_1,
                "wb"
            ) as file:

                file.write(
                    b"duplicate content"
                )

            with open(
                file_2,
                "wb"
            ) as file:

                file.write(
                    b"duplicate content"
                )

            files = [
                {
                    "name": "file1.txt",
                    "path": file_1,
                    "extension": ".txt",
                    "size": os.path.getsize(file_1),
                    "category": "Documents"
                },
                {
                    "name": "file2.txt",
                    "path": file_2,
                    "extension": ".txt",
                    "size": os.path.getsize(file_2),
                    "category": "Documents"
                }
            ]

            duplicates = find_duplicates(
                files
            )

            self.assertEqual(
                len(duplicates),
                1
            )

            self.assertEqual(
                len(duplicates[0]["files"]),
                2
            )

    def test_scan(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            file_1 = os.path.join(
                temp_dir,
                "photo.jpg"
            )

            file_2 = os.path.join(
                temp_dir,
                "document.pdf"
            )

            with open(
                file_1,
                "wb"
            ) as file:

                file.write(
                    b"image"
                )

            with open(
                file_2,
                "wb"
            ) as file:

                file.write(
                    b"document"
                )

            results = scan(
                temp_dir
            )

            self.assertEqual(
                results["total_files"],
                2
            )

            self.assertEqual(
                results["categories"],
                2
            )

            self.assertIn(
                "Images",
                results["category_counts"]
            )

            self.assertIn(
                "Documents",
                results["category_counts"]
            )

            self.assertGreater(
                results["total_size"],
                0
            )


if __name__ == "__main__":
    unittest.main()
