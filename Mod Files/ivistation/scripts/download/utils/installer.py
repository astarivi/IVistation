import os
import zipfile


def install_zip(zip_file, root_dir):
    """
    Installs a Zip file to the given path, file by file. If the
    file exists, it's replaced. It's done in this fashion to
    provide file based percentages (which isn't a great thing but
    that's all we have) and the current file. It also ensures that
    existing files are replaced.

    Args:
        zip_file: Full path to the zip file to install
        root_dir: Full path to the zip file destination
    Returns:
        Yields the progress as an int, and current file as a string
    """

    with zipfile.ZipFile(zip_file, "r") as install_file:
        relative_paths = install_file.namelist()
        total_files = float(len(relative_paths))
        current_file = 0

        for file_path in relative_paths:
            current_file += 1
            # We yield at the start to avoid code repetition
            yield int((current_file / total_files) * 100), file_path

            # Folder
            if file_path.endswith("/"):
                target_folder = os.path.join(
                    root_dir,
                    # Make it Windows compatible just in case
                    file_path.replace("/", "\\")
                )

                # We're good
                if os.path.isdir(target_folder):
                    continue

                # Create the folder
                try:
                    os.makedirs(target_folder)
                except Exception as e:
                    print(
                        "Failed to install zip file ",
                        zip_file,
                        " Requested dir structure couldn't be created: ",
                        target_folder,
                        " due to: ",
                        e
                    )
                    raise e

                continue

            # File
            target_file = os.path.join(
                root_dir,
                # Make it Windows compatible just in case we have file in nested dirs
                file_path.replace("/", "\\")
            )

            try:
                if os.path.isfile(target_file):
                    os.remove(target_file)
            except Exception as e:
                print(
                    "Failed to install zip file ",
                    zip_file,
                    " Requested file couldn't be replaced: ",
                    target_file,
                    " due to: ",
                    e
                )
                raise e

            install_file.extract(file_path, root_dir)

    # Last yield to make sure we get all the files
    yield 100, ""
