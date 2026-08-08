import os
import shutil


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

    moved_files = []
    errors = []

    for file_data in files:

        source_path = file_data.get("path")
        category = file_data.get("category", "Other")

        if not source_path:
            continue

        # Make sure the source still exists
        if not os.path.isfile(source_path):
            continue

        # ==========================================
        # Create Category Folder
        # ==========================================

        category_folder = os.path.join(
            folder_path,
            category
        )

        try:
            os.makedirs(
                category_folder,
                exist_ok=True
            )
        except OSError as error:

            errors.append({
                "name": os.path.basename(source_path),
                "error": str(error)
            })

            continue

        # ==========================================
        # Destination
        # ==========================================

        file_name = os.path.basename(source_path)

        destination_path = os.path.join(
            category_folder,
            file_name
        )

        # ==========================================
        # Prevent Moving Onto Itself
        # ==========================================

        if os.path.abspath(source_path) == os.path.abspath(
            destination_path
        ):
            continue

        try:

            # ==========================================
            # Handle Duplicate File Names
            # ==========================================

            if os.path.exists(destination_path):

                name, extension = os.path.splitext(
                    file_name
                )

                counter = 1

                while os.path.exists(destination_path):

                    new_name = (
                        f"{name}_{counter}{extension}"
                    )

                    destination_path = os.path.join(
                        category_folder,
                        new_name
                    )

                    counter += 1

            # ==========================================
            # Move File
            # ==========================================

            shutil.move(
                source_path,
                destination_path
            )

            # ==========================================
            # Store Exact Move Information
            # ==========================================

            moved_files.append({
                "name": file_name,
                "category": category,
                "source": source_path,
                "destination": destination_path
            })

        except Exception as error:

            errors.append({
                "name": file_name,
                "error": str(error)
            })

    return {
        "moved": moved_files,
        "errors": errors
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

    restored = []
    errors = []

    for file_data in moved_files:

        source = file_data.get("source")
        destination = file_data.get("destination")
        name = file_data.get("name", os.path.basename(destination or ""))

        # ==========================================
        # Validate Record
        # ==========================================

        if not source or not destination:

            errors.append({
                "name": name or "unknown",
                "error": "Missing source or destination path in history record."
            })

            continue

        # ==========================================
        # File Must Still Exist At Destination
        # ==========================================

        if not os.path.isfile(destination):

            errors.append({
                "name": name,
                "error": f"File no longer exists at destination: {destination}"
            })

            continue

        try:

            # ==========================================
            # Recreate Original Directory If Needed
            # ==========================================

            original_dir = os.path.dirname(source)

            os.makedirs(
                original_dir,
                exist_ok=True
            )

            # ==========================================
            # Do Not Overwrite An Existing File
            # ==========================================

            if os.path.exists(source):

                errors.append({
                    "name": name,
                    "error": (
                        f"Original location already occupied, "
                        f"will not overwrite: {source}"
                    )
                })

                continue

            # ==========================================
            # Move File Back To Original Location
            # ==========================================

            shutil.move(destination, source)

            restored.append({
                "name": name,
                "source": source,
                "destination": destination
            })

        except Exception as error:

            errors.append({
                "name": name,
                "error": str(error)
            })

    return {
        "restored": restored,
        "errors": errors
    }