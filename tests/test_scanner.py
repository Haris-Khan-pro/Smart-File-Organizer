import os
import tempfile
import unittest

from app.core.scanner import (
    calculate_file_hash,
    find_duplicates,
    get_category,
    scan,
)


class TestScanner(unittest.TestCase):

    def test_calculate_file_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")

            with open(file_path, "wb") as file:
                file.write(b"hello world")

            file_hash = calculate_file_hash(file_path)

            self.assertIsNotNone(file_hash)
            self.assertEqual(len(file_hash), 64)

    def test_find_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_1 = os.path.join(temp_dir, "file1.txt")
            file_2 = os.path.join(temp_dir, "file2.txt")

            with open(file_1, "wb") as file:
                file.write(b"same content")

            with open(file_2, "wb") as file:
                file.write(b"same content")

            files = [
                {
                    "name": "file1.txt",
                    "path": file_1,
                    "extension": ".txt",
                    "size": os.path.getsize(file_1),
                    "category": "Documents",
                },
                {
                    "name": "file2.txt",
                    "path": file_2,
                    "extension": ".txt",
                    "size": os.path.getsize(file_2),
                    "category": "Documents",
                },
            ]

            duplicates = find_duplicates(files)

            self.assertEqual(len(duplicates), 1)
            self.assertEqual(len(duplicates[0]["files"]), 2)

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
        self.assertEqual(get_category(".PY"), "Code")

    def test_scan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")

            with open(file_path, "wb") as file:
                file.write(b"hello")

            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 1)
            self.assertEqual(results["categories"], 1)
            self.assertEqual(results["category_counts"]["Documents"], 1)
            self.assertEqual(results["total_size"], 5)

    def test_scan_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 0)
            self.assertEqual(results["categories"], 0)
            self.assertEqual(results["total_size"], 0)
            self.assertEqual(results["duplicate_groups"], 0)
            self.assertEqual(results["duplicate_files"], 0)

    def test_scan_invalid_folder_returns_empty_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = os.path.join(temp_dir, "missing_folder")

            results = scan(missing_path)

            self.assertEqual(results["total_files"], 0)
            self.assertEqual(results["categories"], 0)
            self.assertEqual(results["total_size"], 0)
            self.assertEqual(results["duplicate_groups"], 0)
            self.assertEqual(results["duplicate_files"], 0)

    def test_scan_empty_file_and_unicode_space_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_path = os.path.join(temp_dir, "empty.txt")
            unicode_path = os.path.join(temp_dir, "Résumé report 2024.TXT")

            with open(empty_path, "wb") as file:
                file.write(b"")

            with open(unicode_path, "wb") as file:
                file.write(b"hello unicode")

            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 2)
            self.assertEqual(results["category_counts"]["Documents"], 2)
            self.assertEqual(results["files"][0]["size"], 0)

    def test_unknown_extension_is_other(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "unknown.xyz")

            with open(file_path, "wb") as file:
                file.write(b"unknown file")

            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 1)
            self.assertEqual(results["categories"], 1)
            self.assertEqual(results["category_counts"]["Other"], 1)
            self.assertEqual(results["files"][0]["category"], "Other")

    def test_scan_nested_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = os.path.join(temp_dir, "nested", "deep")
            os.makedirs(nested_dir)

            file_path = os.path.join(nested_dir, "nested.txt")

            with open(file_path, "wb") as file:
                file.write(b"nested file")

            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 1)
            self.assertEqual(results["files"][0]["name"], "nested.txt")
            self.assertEqual(
                os.path.abspath(results["files"][0]["path"]),
                os.path.abspath(file_path),
            )

    def test_same_size_different_content_are_not_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_1 = os.path.join(temp_dir, "file1.txt")
            file_2 = os.path.join(temp_dir, "file2.txt")

            with open(file_1, "wb") as file:
                file.write(b"AAAA")

            with open(file_2, "wb") as file:
                file.write(b"BBBB")

            files = [
                {
                    "name": "file1.txt",
                    "path": file_1,
                    "extension": ".txt",
                    "size": 4,
                    "category": "Documents",
                },
                {
                    "name": "file2.txt",
                    "path": file_2,
                    "extension": ".txt",
                    "size": 4,
                    "category": "Documents",
                },
            ]

            duplicates = find_duplicates(files)

            self.assertEqual(len(duplicates), 0)

    def test_multiple_duplicate_groups(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            contents = {
                "a1.txt": b"AAAA",
                "a2.txt": b"AAAA",
                "b1.txt": b"BBBBBBBB",
                "b2.txt": b"BBBBBBBB",
            }

            files = []

            for filename, content in contents.items():
                file_path = os.path.join(temp_dir, filename)

                with open(file_path, "wb") as file:
                    file.write(content)

                files.append({
                    "name": filename,
                    "path": file_path,
                    "extension": ".txt",
                    "size": len(content),
                    "category": "Documents",
                })

            duplicates = find_duplicates(files)

            self.assertEqual(len(duplicates), 2)

            duplicate_file_count = sum(
                len(group["files"])
                for group in duplicates
            )

            self.assertEqual(duplicate_file_count, 4)

    def test_three_identical_files_form_one_group(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []

            for index in range(3):
                file_path = os.path.join(
                    temp_dir,
                    f"duplicate_{index}.txt",
                )

                with open(file_path, "wb") as file:
                    file.write(b"same content")

                file_paths.append(file_path)

            files = [
                {
                    "name": os.path.basename(file_path),
                    "path": file_path,
                    "extension": ".txt",
                    "size": os.path.getsize(file_path),
                    "category": "Documents",
                }
                for file_path in file_paths
            ]

            duplicates = find_duplicates(files)

            self.assertEqual(len(duplicates), 1)
            self.assertEqual(len(duplicates[0]["files"]), 3)
            self.assertEqual(
                duplicates[0]["size"],
                len(b"same content"),
            )
            self.assertTrue(
                all(
                    file_data["size"] == len(b"same content")
                    for file_data in duplicates[0]["files"]
                )
            )

    def test_scan_duplicate_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original = os.path.join(temp_dir, "original.txt")
            duplicate = os.path.join(temp_dir, "duplicate.txt")
            unique = os.path.join(temp_dir, "unique.txt")

            with open(original, "wb") as file:
                file.write(b"duplicate")

            with open(duplicate, "wb") as file:
                file.write(b"duplicate")

            with open(unique, "wb") as file:
                file.write(b"unique")

            results = scan(temp_dir)

            self.assertEqual(results["total_files"], 3)
            self.assertEqual(results["duplicate_groups"], 1)
            self.assertEqual(results["duplicate_files"], 2)


if __name__ == "__main__":
    unittest.main()
