import os
import sqlite3

from contextlib import closing


class DatabaseHelper:
    def __init__(self, database):
        self.database = database

        if not os.path.exists(database):
            print("The content database '{}' doesn't exist.".format(database))
            return

        self.db_connection = sqlite3.connect(database)

    def get_title_from_crc32(self, crc32):
        with closing(self.db_connection.cursor()) as cursor:
            select_query = '''
                SELECT title FROM root WHERE crc = ?;
            '''

            cursor.execute(select_query, (crc32,))

            row = cursor.fetchone()

            if row is not None:
                return row[0]

            return None

    def close(self):
        if hasattr(self, 'db_connection') and self.db_connection is not None:
            self.db_connection.close()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            print("Couldn't destroy database helper for {}".format(self.database), e)
