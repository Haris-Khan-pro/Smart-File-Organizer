import os
import hashlib

from app.core.logger import logger

# ==========================================
# File Categories
# ==========================================

FILE_CATEGORIES = {

    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".ico",
        ".tiff",
        ".tif"
    },

    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".csv",
        ".ppt",
        ".pptx"
    },

    "Videos": {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v"
    },

    "Audio": {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma"
    },

    "Archives": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2"
    },

    "Code": {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".html",
        ".css",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".php",
        ".go",
        ".rs",
        ".rb",
        ".sql"
    },

    "Executables": {
        ".exe",
        ".msi",
        ".bat",
        ".cmd",
        ".sh"
    }
}


# ==========================================
# Determine Category
# ==========================================

def get_category(extension):

    if not extension:
        return "Other"

    normalized_extension = str(extension).lower()

    if not normalized_extension.startswith("."):
        normalized_extension = f".{normalized_extension}"

    for category, extensions in FILE_CATEGORIES.items():

        if normalized_extension in extensions:
            return category

    return "Other"


# ==========================================
# Calculate File Hash
# ==========================================

def calculate_file_hash(file_path, chunk_size=1024 * 1024):
    """
    Calculate SHA-256 hash of a file.

    Files with the same SHA-256 hash have
    identical content.
    """

    if not file_path or not os.path.isfile(file_path):
        return None

    sha256 = hashlib.sha256()

    try:

        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(chunk_size)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
        ValueError
    ):

        return None


# ==========================================
# Find Duplicate Files
# ==========================================

def find_duplicates(files):
    """
    Find files with identical content.

    Uses file size as a quick first check,
    then SHA-256 hashing for confirmation.

    Returns:
        [
            {
                "hash": "...",
                "size": 12345,
                "files": [
                    {
                        "name": "...",
                        "path": "..."
                    }
                ]
            }
        ]
    """

    # ==========================================
    # Group By File Size
    # ==========================================

    size_groups = {}

    for file_data in files:

        file_path = file_data.get("path")
        file_size = file_data.get("size", 0)

        if not file_path:
            continue

        if not os.path.isfile(file_path):
            continue

        size_groups.setdefault(
            file_size,
            []
        ).append(file_data)

    # ==========================================
    # Only Same-Size Files Can Be Duplicates
    # ==========================================

    duplicate_groups = []

    for file_size, same_size_files in size_groups.items():

        # A single file cannot be a duplicate
        if len(same_size_files) < 2:
            continue

        hash_groups = {}

        # ==========================================
        # Calculate Hash
        # ==========================================

        for file_data in same_size_files:

            file_path = file_data["path"]

            file_hash = calculate_file_hash(
                file_path
            )

            if file_hash is None:
                continue

            hash_groups.setdefault(
                file_hash,
                []
            ).append(file_data)

        # ==========================================
        # Keep Only Actual Duplicates
        # ==========================================

        for file_hash, matching_files in hash_groups.items():

            if len(matching_files) < 2:
                continue

            duplicate_groups.append({
                "hash": file_hash,
                "size": file_size,
                "files": [
                    {
                        "name": file_data["name"],
                        "path": file_data["path"],
                        "size": file_data.get("size", file_size)
                    }
                    for file_data in matching_files
                ]
            })

    return duplicate_groups


# ==========================================
# Scan Folder
# ==========================================

def scan(folder_path):

    if not folder_path or not os.path.isdir(folder_path):
        logger.warning("Scan requested for invalid folder: %s", folder_path)
        return {
            "files": [],
            "total_files": 0,
            "categories": 0,
            "category_counts": {},
            "total_size": 0,
            "duplicates": [],
            "duplicate_groups": 0,
            "duplicate_files": 0,
        }

    files = []
    category_counts = {}
    total_size = 0

    logger.info("Scan started for folder: %s", folder_path)

    try:
        for root, directories, filenames in os.walk(folder_path, followlinks=False):
            directories[:] = [
                directory for directory in directories
                if not os.path.islink(os.path.join(root, directory))
            ]

            for filename in filenames:
                file_path = os.path.join(root, filename)

                if os.path.islink(file_path):
                    continue

                try:
                    if not os.path.isfile(file_path):
                        continue

                    file_size = os.path.getsize(file_path)
                except (FileNotFoundError, PermissionError, OSError):
                    logger.warning("Skipping unreadable file during scan: %s", file_path)
                    continue

                _, extension = os.path.splitext(filename)
                category = get_category(extension)

                file_record = {
                    "name": filename,
                    "path": file_path,
                    "extension": extension,
                    "size": file_size,
                    "category": category,
                }

                files.append(file_record)
                category_counts[category] = category_counts.get(category, 0) + 1
                total_size += file_size
    except OSError as error:
        logger.error("Scan failed for folder %s: %s", folder_path, error)
        files = []
        category_counts = {}
        total_size = 0

    duplicate_groups = find_duplicates(files)
    duplicate_file_count = sum(
        len(group["files"])
        for group in duplicate_groups
    )

    logger.info(
        "Scan complete for %s: %s files, %s duplicate groups",
        folder_path,
        len(files),
        len(duplicate_groups),
    )

    return {
        "files": files,
        "total_files": len(files),
        "categories": len(category_counts),
        "category_counts": category_counts,
        "total_size": total_size,
        "duplicates": duplicate_groups,
        "duplicate_groups": len(duplicate_groups),
        "duplicate_files": duplicate_file_count,
    }