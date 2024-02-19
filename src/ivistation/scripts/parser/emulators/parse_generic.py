import os
import xbmc

from content.db_lookup import DatabaseHelper
from parse_system import ParseSystem

EXTENSION_MATRIX = {
    "gba": ("gba",),
    "gbc": ("gbc", ),
    "gb": ("gb", ),
}


class ParseGeneric(ParseSystem):
    def __init__(self, system, crc_support=True):
        super(ParseGeneric, self).__init__(system)

        self.system = system
        self.content_database = None

        if system not in EXTENSION_MATRIX:
            raise KeyError("This generic system isn't supported " + system)

        self.extensions = EXTENSION_MATRIX[system]

        print("Initializing generic {} parser...".format(system))

        self.path = xbmc.translatePath("Special://root/ivistation/roms/" + system)

        print("Generic {} roms path: ".format(system), self.path)

        content_database = xbmc.translatePath("Special://root/ivistation/data/content_db/{}.db".format(system))

        self.crc32_support = crc_support and os.path.isfile(content_database)

        if self.crc32_support:
            print("Generic {} content database location: ".format(system), content_database)
            self.content_database = DatabaseHelper(content_database)

    def _use_crc32(self):
        return self.crc32_support

    def _get_path(self):
        return self.path

    def _get_allowed_extensions(self):
        return self.extensions

    def _get_title_from_crc32(self, crc32):
        return self.content_database.get_title_from_crc32(crc32)

    def finalize(self):
        self.content_database.close()
