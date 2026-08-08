import os
import shutil


def organize(folder_path, files):
    """
    Organize scanned files into category folders.
    """

    moved_files = []
    errors = []

    for file_data in files:

        source_path = file_data["path"]
        category = file_data.get("category", "Other")

        if not os.path.isfile(source_path):
            continue

        # Create category folder
        category_folder = os.path.join(
            folder_path,
            category
        )

        os.makedirs(
            category_folder,
            exist_ok=True
        )

        # Destination
        file_name = os.path.basename(source_path)
        destination_path = os.path.join(
            category_folder,
            file_name
        )

        # Avoid moving a file onto itself
        if os.path.abspath(source_path) == os.path.abspath(destination_path):
            continue

        try:

            # Handle duplicate filenames
            if os.path.exists(destination_path):

                name, extension = os.path.splitext(file_name)

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

            shutil.move(
                source_path,
                destination_path
            )

            moved_files.append({
                "name": file_name,
                "category": category,
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