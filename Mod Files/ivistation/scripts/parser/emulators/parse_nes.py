import os
import zlib

import xbmc

from content.db_lookup import DatabaseHelper
from parse_system import ParseSystem

ALLOWED_EXTENSIONS = (
    "nes"
)


class ParseNES(ParseSystem):
    def __init__(self):
        ParseSystem.__init__(self)
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

    @staticmethod
    def _get_rom_crc32(rom_path):
        with open(rom_path, 'rb') as rom_file:
            rom_data = rom_file.read()

            # Header found
            if rom_data[:3] == b'NES':
                # Remove the header
                clean_rom_data = rom_data[16:]
            else:
                # Parse the ROM as is
                clean_rom_data = rom_data

            crc32_value = zlib.crc32(clean_rom_data) & 0xFFFFFFFF

            return "{:08x}".format(crc32_value).lower()

    def finalize(self):
        self.content_database.close()
