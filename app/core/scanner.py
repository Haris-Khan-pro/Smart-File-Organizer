import os
import hashlib

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

    extension = extension.lower()

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:
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
        PermissionError,
        OSError
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
                        "path": file_data["path"]
                    }
                    for file_data in matching_files
                ]
            })

    return duplicate_groups


# ==========================================
# Scan Folder
# ==========================================

def scan(folder_path):

    files = []

    category_counts = {}

    total_size = 0

    # ==========================================
    # Walk Through Folder
    # ==========================================

    for root, directories, filenames in os.walk(folder_path):

        for filename in filenames:

            file_path = os.path.join(
                root,
                filename
            )

            try:

                file_size = os.path.getsize(
                    file_path
                )

                _, extension = os.path.splitext(
                    filename
                )

                category = get_category(
                    extension
                )

                # ==========================================
                # Store File Information
                # ==========================================

                files.append({
                    "name": filename,
                    "path": file_path,
                    "extension": extension,
                    "size": file_size,
                    "category": category
                })

                # ==========================================
                # Update Category Count
                # ==========================================

                category_counts[category] = (
                    category_counts.get(
                        category,
                        0
                    ) + 1
                )

                # ==========================================
                # Update Total Size
                # ==========================================

                total_size += file_size

            except (
                PermissionError,
                OSError
            ):

                # Skip files we cannot access
                continue

    # ==========================================
    # Find Duplicates
    # ==========================================

    duplicate_groups = find_duplicates(
        files
    )

    # ==========================================
    # Count Duplicate Files
    # ==========================================

    duplicate_file_count = sum(
        len(group["files"])
        for group in duplicate_groups
    )

    # ==========================================
    # Return Scan Results
    # ==========================================

    return {
        "files": files,
        "total_files": len(files),
        "categories": len(category_counts),
        "category_counts": category_counts,
        "total_size": total_size,

        # Duplicate information
        "duplicates": duplicate_groups,
        "duplicate_groups": len(
            duplicate_groups
        ),
        "duplicate_files": duplicate_file_count
    }