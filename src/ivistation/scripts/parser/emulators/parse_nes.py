import os
import xbmc

from content.db_lookup import DatabaseHelper
from parse_system import ParseSystem

ALLOWED_EXTENSIONS = (
    "nes"
)


class ParseNES(ParseSystem):
    def __init__(self):
        super(ParseNES, self).__init__("nes")

        print("Initializing NES parser...")

        root_path = xbmc.translatePath("Special://root/")

        self.path = os.path.join(
            root_path,
            "ivistation\\roms\\nes"
        )

        print("NES roms path: ", self.path)

        content_database = os.path.join(
            root_path,
            "ivistation\\data\\content_db\\nes.db"
        )

        print("NES content database location: ", content_database)

        self.content_database = DatabaseHelper(content_database)

    def _get_path(self):
        return self.path

    def _get_allowed_extensions(self):
        return ALLOWED_EXTENSIONS

    def _get_title_from_crc32(self, crc32):
        return self.content_database.get_title_from_crc32(crc32)

    def _get_rom_crc32(self, file_handle, chunk_size=8192):
        header_data = file_handle.read(3)

        # Header found
        if header_data == b'NES':
            # Remove the header
            file_handle.seek(16)
        else:
            file_handle.seek(0)

        return super(ParseNES, self)._get_rom_crc32(file_handle)

    def finalize(self):
        self.content_database.close()
