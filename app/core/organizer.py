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