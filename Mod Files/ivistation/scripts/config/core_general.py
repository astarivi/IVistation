import os
import shutil
import zipfile

from content_config import get_core_path


def reset_core_to_defaults(emu_system, core, core_info):
    """
    Resets core settings to default while keeping user saves.
    """
    core_path = get_core_path(emu_system, core)

    if "backup" not in core_info:
        print("Request core reset for ", core, " failed as backup file wasn't declared in info.json file")
        return False

    backup_file_path = os.path.join(
        core_path,
        core_info["backup"]
    )

    # It doesn't exist
    if not os.path.isfile(backup_file_path):
        print("Request core reset for ", core, " failed as backup file does not exist: ", backup_file_path)
        return False

    # Open the zipfile
    with zipfile.ZipFile(backup_file_path, "r") as backup_file:
        relative_paths = backup_file.namelist()

        # Remove the old files
        for file_path in relative_paths:
            # Folder
            if file_path.endswith("/"):
                target_folder = os.path.join(
                    core_path,
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
                        "Failed to reset core ",
                        core,
                        " to defaults. Request dir structure couldn't be created: ",
                        target_folder,
                        " due to: ",
                        e
                    )

                continue

            # File

            target_file = os.path.join(
                core_path,
                # Make it Windows compatible just in case we have file in nested dirs
                file_path.replace("/", "\\")
            )

            if not os.path.isfile(target_file):
                continue

            try:
                os.remove(target_file)
            except Exception as e:
                print(
                    "Failed to reset core ",
                    core,
                    " to defaults. Request file couldn't be removed: ",
                    target_file,
                    " due to: ",
                    e
                )

        # Extract the contents
        try:
            backup_file.extractall(core_path)
            return True
        except Exception as e:
            print(
                "Failed to reset core ",
                core,
                " to defaults. Backup file couldn't extract: ",
                backup_file_path,
                " due to: ",
                e
            )

    return False


def delete_core_data(emu_system, core, core_info):
    """
    Removes all the data for this core, including saves, and then places a fresh copy of the default settings back.
    """
    core_path = get_core_path(emu_system, core)

    if "data_folder" not in core_info:
        print("Failed to delete core data, as 'data_folder' key wasn't found in core_info.json")
        return False

    data_folder_path = os.path.join(
        core_path,
        core_info["data_folder"]
    )

    if not os.path.isdir(data_folder_path):
        os.makedirs(data_folder_path)
        return reset_core_to_defaults(emu_system, core, core_info)

    try:
        shutil.rmtree(data_folder_path)
    except Exception as e:
        print("Failed to remove directory tree ", data_folder_path, " for core reset of ", core, " due to ", e)
    finally:
        return reset_core_to_defaults(emu_system, core, core_info)
