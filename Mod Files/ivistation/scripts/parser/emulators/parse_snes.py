import os
import zlib

import xbmc

from content.db_lookup import DatabaseHelper
from parse_system import ParseSystem

ALLOWED_EXTENSIONS = (
    "sfc",
    "smc"
)


class ParseSNES(ParseSystem):
    def __init__(self):
        ParseSystem.__init__(self)
        print("Initializing SNES parser...")

        root_path = xbmc.translatePath("Special://root/")

        self.path = os.path.join(
            root_path,
            "ivistation\\roms\\snes"
        )

        print("SNES roms path: ", self.path)

        content_database = os.path.join(
            root_path,
            "ivistation\\data\\content_db\\snes.db"
        )

        print("SNES content database location: ", content_database)

        self.content_database = DatabaseHelper(content_database)

    def _get_path(self):
        return self.path

    def _get_allowed_extensions(self):
        return ALLOWED_EXTENSIONS

    def _get_title_from_crc32(self, crc32):
        return self.content_database.get_title_from_crc32(crc32)

    @staticmethod
    def _get_rom_crc32(rom_path):
        # Will be 0 if the rom is SFC, or the size of the header if it's SMC
        smc_header_size = os.path.getsize(rom_path) % 1024

        with open(rom_path, 'rb') as rom_file:
            # Skip the header
            if smc_header_size != 0:
                rom_file.seek(smc_header_size)

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
