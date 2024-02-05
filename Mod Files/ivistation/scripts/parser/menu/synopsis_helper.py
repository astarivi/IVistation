import os
import xbmc
import zlib
import sqlite3
import xml.sax.saxutils

from ivistation.utils import clean_rom_name

DEFAULT_GAME_DETAILS = '''Name: {}
Platform: {}
Region: Unknown
Media: Unknown
Release Year: Unknown
Developer: Unknown
Publisher: Unknown
Players: At least 1
Identifier: {}'''


class SynopsisHelper(object):
    enabled = True

    def __init__(self, system):
        self.system = system
        self.db_path = os.path.join(
            xbmc.translatePath("Special://root/ivistation/data/synopsis"),
            system + ".db"
        )

        if not os.path.isfile(self.db_path):
            print("The synopsis database for '{}' doesn't exist.".format(self.system))
            self.enabled = False
            return

        self.db_connection = sqlite3.connect(self.db_path)

    def get_synopsis(self, name, crc32=None):
        """
        Retrieves the synopsis from the db file, by trying the CRC32 code first,
        then the name.

        This function may be called if the rom isn't in no-intro standard, but the
        chances it finds anything matching in database are slim to none.

        Args:
            name: Rom filename in no-intro standard
            crc32: CRC32 of this ROM (optional)
        Returns:
            (game_details, game_synopsis): tuple of the split synopsis.
        """
        cursor = self.db_connection.cursor()

        # Try CRC32 first, only if we have it, and the database supports it
        if crc32 is not None and self._table_exists(cursor, "crc"):
            crc_select_query = '''
                    SELECT root_id FROM crc WHERE crc = ?;
                '''

            cursor.execute(crc_select_query, (crc32,))
            row = cursor.fetchone()

            if row is not None:
                id_select_query = '''
                        SELECT synopsis FROM root WHERE id = ?;
                    '''
                cursor.execute(id_select_query, (row[0],))

                return self._parse_synopsis(cursor.fetchone()[0])

        # Try by name
        for column in ["name", "xtrasname"]:
            select_query = '''
                SELECT synopsis FROM root WHERE {} = ?;
            '''.format(column)

            cursor.execute(select_query, (clean_rom_name(name),))

            row = cursor.fetchone()

            if row is None:
                continue

            return self._parse_synopsis(row[0])

        raise ValueError

    @staticmethod
    def _table_exists(cursor, table_name):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    @staticmethod
    def _parse_synopsis(raw_synopsis):
        decoded_synopsis = xml.sax.saxutils.escape(zlib.decompress(str(raw_synopsis)).decode('utf-8'))

        return decoded_synopsis.split("_________________________")[:2]

    def close(self):
        if hasattr(self, 'db_connection') and self.db_connection is not None:
            self.db_connection.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            print("Couldn't destroy database helper for {}".format(self.database))
