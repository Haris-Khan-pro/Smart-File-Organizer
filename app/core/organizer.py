import os
import shutil

from app.core.logger import logger


def organize(folder_path, files):
    """
    Organize scanned files into category folders.

    Returns:
        {
            "moved": [
                {
                    "name": original filename,
                    "category": category name,
                    "source": original full path,
                    "destination": new full path
                }
            ],
            "errors": [...]
        }
    """

    if not isinstance(files, list):
        logger.warning("Organization rejected because file list is invalid: %s", type(files).__name__)
        return {
            "moved": [],
            "errors": [{
                "name": "unknown",
                "error": "File list is invalid or missing."
            }],
        }

    moved_files = []
    errors = []

    logger.info("Organization started for folder: %s with %s files", folder_path, len(files))

    for file_data in files:

        if not isinstance(file_data, dict):
            errors.append({
                "name": "unknown",
                "error": "Invalid file record in organize input."
            })
            continue

        source_path = file_data.get("path")
        category = file_data.get("category", "Other")
        file_name = file_data.get("name") or os.path.basename(source_path or "")

        if not source_path:
            logger.warning("Organization skipped file with missing source path: %s", file_name)
            errors.append({
                "name": file_name or "unknown",
                "error": "Missing source path in file record."
            })
            continue

        if not os.path.isfile(source_path):
            logger.warning("Organization skipped missing file: %s", source_path)
            errors.append({
                "name": file_name or "unknown",
                "error": f"Source file no longer exists: {source_path}"
            })
            continue

        category_folder = os.path.join(folder_path, category)

        try:
            os.makedirs(category_folder, exist_ok=True)
        except OSError as error:
            logger.error("Failed to create category folder %s: %s", category_folder, error)
            errors.append({
                "name": file_name,
                "error": str(error)
            })
            continue

        destination_path = os.path.join(category_folder, file_name)

        if os.path.abspath(source_path) == os.path.abspath(destination_path):
            continue

        try:
            if os.path.exists(destination_path):
                name, extension = os.path.splitext(file_name)
                counter = 1

                while os.path.exists(destination_path):
                    new_name = f"{name}_{counter}{extension}"
                    destination_path = os.path.join(category_folder, new_name)
                    counter += 1

            shutil.move(source_path, destination_path)

            moved_files.append({
                "name": file_name,
                "category": category,
                "source": source_path,
                "destination": destination_path,
            })
            logger.info("Moved file %s -> %s", source_path, destination_path)

        except (OSError, shutil.Error, ValueError) as error:
            logger.error("Failed to move file %s to %s: %s", source_path, destination_path, error)
            errors.append({
                "name": file_name,
                "error": str(error)
            })

    logger.info("Organization complete for %s: %s moved, %s errors", folder_path, len(moved_files), len(errors))

    return {
        "moved": moved_files,
        "errors": errors,
    }


def undo_organization(moved_files):
    """
    Restore previously organized files to their original locations.

    Parameters:
        moved_files (list): List of move records, each containing:
            - "source":      original file path before organization
            - "destination": file path after organization

    Returns:
        {
            "restored": [
                {
                    "name": filename,
                    "source": original path,
                    "destination": path it was moved from
                }
            ],
            "errors": [
                {
                    "name": filename or path,
                    "error": error message
                }
            ]
        }
    """

    if not isinstance(moved_files, list):
        logger.warning("Undo rejected because history is invalid: %s", type(moved_files).__name__)
        return {
            "restored": [],
            "errors": [{
                "name": "unknown",
                "error": "Operation history is invalid or missing."
            }],
        }

    restored = []
    errors = []

    logger.info("Undo started for %s history entries", len(moved_files))

    for file_data in moved_files:

        if not isinstance(file_data, dict):
            errors.append({
                "name": "unknown",
                "error": "Invalid history record in undo operation."
            })
            continue

        source = file_data.get("source")
        destination = file_data.get("destination")
        name = file_data.get("name", os.path.basename(destination or ""))

        if not source or not destination:
            errors.append({
                "name": name or "unknown",
                "error": "Missing source or destination path in history record."
            })
            continue

        if not os.path.isfile(destination):
            logger.warning("Undo skipped missing destination: %s", destination)
            errors.append({
                "name": name,
                "error": f"File no longer exists at destination: {destination}"
            })
            continue

        try:
            original_dir = os.path.dirname(source)
            os.makedirs(original_dir, exist_ok=True)

            if os.path.exists(source):
                logger.warning("Undo blocked by existing file at original location: %s", source)
                errors.append({
                    "name": name,
                    "error": (
                        f"Original location already occupied, "
                        f"will not overwrite: {source}"
                    )
                })
                continue

            shutil.move(destination, source)

            restored.append({
                "name": name,
                "source": source,
                "destination": destination,
            })
            logger.info("Restored file %s -> %s", destination, source)

        except (OSError, shutil.Error, ValueError) as error:
            logger.error("Undo failed for %s: %s", destination, error)
            errors.append({
                "name": name,
                "error": str(error)
            })

    logger.info("Undo complete: %s restored, %s errors", len(restored), len(errors))

    return {
        "restored": restored,
        "errors": errors
    }