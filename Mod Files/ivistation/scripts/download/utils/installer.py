import os
import sys
import zlib
import xbmc
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


def calculate_crc32(file_path, chunk_size=8192, progress_threshold_kb=512):
    """
    Calculates the CRC32 of a given file, with the given chunk_size.

    Args:
        file_path: str absolute path to file
        chunk_size: int chunk size for file read ops
        progress_threshold_kb: int, every how many calculated kbs to yield progress
    Returns:
        Yields int progress, and str crc32 checksum (empty if not done)
    """
    progress_threshold = progress_threshold_kb * 1024

    with open(file_path, "rb") as file_handle:
        file_size = float(os.path.getsize(file_path))
        bytes_read = 0
        bytes_since_last_callback = 0
        crc32_checksum = 0

        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            crc32_checksum = zlib.crc32(chunk, crc32_checksum)

            chk_length = len(chunk)
            bytes_read += chk_length
            bytes_since_last_callback += chk_length

            if bytes_since_last_callback >= progress_threshold:
                progress = min(100, int(bytes_read / file_size * 100))
                bytes_since_last_callback = 0

                yield progress, ""

        yield 100, "{:08x}".format(crc32_checksum & 0xFFFFFFFF)


def get_update_installer_version():
    update_xbe_path = xbmc.translatePath("special://root/ivistation/update.xbe")

    if not os.path.isfile(update_xbe_path):
        return -1

    # Add scripts root dir to path, and import from it
    sys.path.append(
        xbmc.translatePath("Special://root/ivistation/scripts/parser/emulators/utils")
    )

    # noinspection PyUnresolvedReferences
    from xbe import XBE

    xbe_info = XBE(update_xbe_path)

    return int(xbe_info.cert.dwVersion)
