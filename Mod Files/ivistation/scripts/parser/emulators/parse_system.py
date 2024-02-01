import os
import zlib
import xbmc
import shutil
import random
import string

from abc import abstractmethod

ALLOWED_FILENAME_CHARACTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&'()-.@[]^_`{}~")
ARTWORK_SUB_FOLDERS = [
    "boxart",
    "boxart3d",
    "logo",
    "mix",
    "screenshots",
    "videos"
]


class ParseSystem(object):
    entries = []

    def __init__(self, system):
        declared_media_path = xbmc.getInfoLabel('skin.string(Custom_Media_Path)')
        root_media_path = os.path.join(declared_media_path, system)

        for sub_folder in ARTWORK_SUB_FOLDERS:
            try:
                os.makedirs(
                    os.path.join(
                        root_media_path,
                        sub_folder
                    )
                )
            except Exception:
                continue

    @staticmethod
    def get_progress_title():
        return "Processing [B]{}[/B] rom files"

    @abstractmethod
    def _get_path(self):
        """
        Provide the path to the roms, in your implementation.
        """
        return ""

    @abstractmethod
    def _get_allowed_extensions(self):
        """
        Provide an iterable of allowed extensions (without the dot) for the target system.

        Ex: nes
        """
        return []

    def _use_crc32(self):
        """
        If your implementation doesn't rely on CRC32, or it's too expensive, override this and return False to
        disable the calculation
        """
        return True

    def _get_title_from_crc32(self, crc32):
        """
        When CRC32 is active, it may be used to check for the right title. Override this method and provide the right
        title. This could be done by looking at a database, such as those from datomatic.

        If CRC32 is active, but this method isn't overriden, the filename will be used.
        """
        return None

    def _get_rom_crc32(self, file_handle, chunk_size=8192):
        """
        Calculates the rom CRC32. The default implementation loads chunks into memory, and slowly but surely calculates
        the checksum. If your implementation needs a different method (as in, skipping header bytes), override this
        and provide your own implementation.
        """
        crc32_checksum = 0

        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            crc32_checksum = zlib.crc32(chunk, crc32_checksum)

        return "{:08x}".format(crc32_checksum & 0xFFFFFFFF)

    def prepare_entries(self):
        """
        Prepares the entries. This process includes renaming the roms to safe names, using CRC32 titles if available,
        and removing invalid files/folders from the input.

        Yields:
            int: Progress of this process.
            str: Title of the last item processed.
        """
        path = self._get_path()
        if path == "":
            yield -1, "Nothing found"

        if not os.path.isdir(path):
            print("Rom folder doesn't exist: {}".format(path))
            print("Creating the rom folder.")
            if os.path.isfile(path):
                os.remove(path)

            os.makedirs(path)

        potential_files = [os.path.join(path, file_name) for file_name in os.listdir(path)]
        valid_files = []

        # Verify what we can use.
        for entry in potential_files:
            full_path_entry = os.path.join(path, entry)
            print(full_path_entry)

            if not os.path.isfile(full_path_entry):
                print("This entry is not a file")
                continue

            if os.path.splitext(entry)[1].lower().replace(".", "") not in self._get_allowed_extensions():
                print("Wrong extension", os.path.splitext(entry)[1].lower())
                continue

            valid_files.append(full_path_entry)

        differences = list(
            set(potential_files) -
            set(valid_files)
        )

        # Remove useless files, if possible
        for difference in differences:
            try:
                if os.path.isfile(difference):
                    os.remove(difference)
                else:
                    shutil.rmtree(difference)
            except Exception:
                print("Failed to delete invalid file/folder {}".format(
                    difference
                ))

        # Rename stuff
        count = 0
        for rom_full_path in valid_files:
            rom_crc32 = None
            title, extension = os.path.splitext(os.path.basename(rom_full_path))

            if self._use_crc32():
                with open(rom_full_path, "rb") as crc_handle:
                    rom_crc32 = self._get_rom_crc32(crc_handle)
                content_title = self._get_title_from_crc32(rom_crc32)

                if content_title is not None:
                    title = content_title
            else:
                title = title.replace("_", " ")

            clean_filename = self.clean_filename(title)

            rom_new_path = os.path.join(path, clean_filename + extension)

            # The new filename already exists. Perhaps they are duplicates?
            if (rom_full_path != rom_new_path) and (os.path.exists(rom_new_path) or rom_new_path in potential_files):
                # Add the current count number to the path to give some uniqueness
                rom_new_path = os.path.join(path, "{}_dup{}{}".format(clean_filename, count, extension))

            try:
                if rom_full_path != rom_new_path:
                    os.rename(rom_full_path, rom_new_path)
            except OSError as e:
                print(
                    "Error while renaming the file: {} to {}".format(
                        rom_full_path,
                        rom_new_path
                    ),
                    e
                )
                print("This file will be ignored.")
                count += 1
                yield int((count / float(len(valid_files))) * 100), "Invalid file, skipping..."
                continue

            self.entries.append(
                (title, rom_crc32, rom_new_path)
            )
            count += 1
            yield int((count / float(len(valid_files))) * 100), title
        yield 100, "Done"

    def count_entries(self):
        return len(self.entries)

    @staticmethod
    def clean_filename(name):
        """
        Returns a clean filename for the file. Why do we apply FATX limitations? Because we
        may use the dat-o-matic no-intro official title for the ROM. We also remove problematic
        stuff in the path, like spaces and commmas
        """
        # Remove spaces and change them for _
        filename = name.lower().replace(" ", "_")

        filename = ''.join(char for char in filename if char in ALLOWED_FILENAME_CHARACTERS)

        # If we killed the filename (whoops), create a random one.
        if filename == "" or filename == " ":
            return "".join(random.choice(string.ascii_lowercase) for _ in range(12))

        return filename[:38]

    def get_entries(self):
        return sorted(self.entries, key=lambda x: x[0])

    @abstractmethod
    def finalize(self):
        pass
