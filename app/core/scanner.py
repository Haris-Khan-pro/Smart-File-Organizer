import os


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

                # Store file information
                files.append({
                    "name": filename,
                    "path": file_path,
                    "extension": extension,
                    "size": file_size,
                    "category": category
                })

                # Update category count
                category_counts[category] = (
                    category_counts.get(
                        category,
                        0
                    ) + 1
                )

                # Update total size
                total_size += file_size

            except (
                PermissionError,
                OSError
            ):

                # Skip files we cannot access
                continue

    # ==========================================
    # Return Scan Results
    # ==========================================

    return {
        "files": files,
        "total_files": len(files),
        "categories": len(category_counts),
        "category_counts": category_counts,
        "total_size": total_size
    }