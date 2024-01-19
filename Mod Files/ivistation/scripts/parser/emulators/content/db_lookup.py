import os
import sqlite3


class DatabaseHelper:
    def __init__(self, database):
        self.database = database

        if not os.path.exists(database):
            print("The content database '{}' doesn't exist.".format(database))
            return

        self.db_connection = sqlite3.connect(database)

    def get_title_from_crc32(self, crc32):
        cursor = self.db_connection.cursor()

        select_query = '''
            SELECT * FROM root WHERE crc = ?;
        '''

        cursor.execute(select_query, (crc32,))

        row = cursor.fetchone()

        if row is not None:
            return row[2]

        return None

    def close(self):
        if self.db_connection is not None:
            self.db_connection.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            print("Couldn't destroy database helper for {}".format(self.database))
