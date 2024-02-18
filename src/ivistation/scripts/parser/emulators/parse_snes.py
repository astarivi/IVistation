import os
import xbmc

from content.db_lookup import DatabaseHelper
from parse_system import ParseSystem

ALLOWED_EXTENSIONS = (
    "sfc",
    "smc"
)


class ParseSNES(ParseSystem):
    def __init__(self):
        super(ParseSNES, self).__init__("snes")

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

    def _get_rom_crc32(self, file_handle, chunk_size=8192):
        smc_header_size = os.path.getsize(file_handle.name) % 1024

        if smc_header_size != 0:
            # Skip the header
            file_handle.seek(smc_header_size)

        return super(ParseSNES, self)._get_rom_crc32(file_handle)

    def finalize(self):
        self.content_database.close()
