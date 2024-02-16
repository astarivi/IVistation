import os
import xbmc
import sqlite3
import simplejson as json

from contextlib import closing

CONFIGS_PATH = xbmc.translatePath("Special://root/ivistation/configs/")


class SettingsDatabaseEntry(object):
    def __init__(self, user_db_connection, identifier):
        if identifier is None:
            raise TypeError("Identifier cannot be empty")

        self._user_db_connection = user_db_connection
        self._identifier = identifier

        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "INSERT OR IGNORE INTO settings (identifier, ignored, asked) VALUES (?, 0, 0);",
                (identifier,)
            )

            self._user_db_connection.commit()

            cursor.execute(
                "SELECT * FROM settings WHERE identifier = ?;",
                (identifier,)
            )

            result = cursor.fetchone()

            if result:
                self.database_id = result[0]
                self._ignored = bool(result[2])
                self._asked = bool(result[3])

        raise LookupError("Identifier {} couldn't be created or retrieved from user database".format(identifier))

    @property
    def identifier(self):
        return self._identifier

    @property
    def ignored(self):
        return self._ignored

    @ignored.setter
    def ignored(self, value):
        if not isinstance(value, bool):
            raise TypeError("Value has to be a boolean")

        self._ignored = value

    @property
    def asked(self):
        return self._asked

    @asked.setter
    def asked(self, value):
        if not isinstance(value, bool):
            raise TypeError("Value has to be a boolean")

        self._asked = value

    def save(self):
        if self._user_db_connection.closed:
            raise EnvironmentError(
                "User overrides database is closed, and we just tried to save override_settings {} to it".format(
                    self.identifier,
                )
            )

        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "UPDATE settings SET ignored = ?, asked = ? WHERE id = ?;",
                (int(self.ignored), int(self.asked), self.database_id,)
            )

            self._user_db_connection.commit()


class DatabaseEntry(object):
    def __init__(self, user_db_connection, override_db_connection, identifier):
        if identifier is None:
            raise TypeError("Identifier cannot be empty")

        self._user_db_connection = user_db_connection
        self._override_db_connection = override_db_connection
        self._identifier = identifier
        self._is_override = False
        self._settings = None

        # Check for user data
        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM root WHERE identifier = ?;",
                (self.identifier,)
            )

            row = cursor.fetchone()

            if row is not None:
                self._database_id = row[0]
                self.json_data = json.loads(row[2])
                return

        # Check for override data
        if self._override_db_connection is None:
            # Populate an empty object
            self._database_id = None
            self.json_data = {}
            return

        with closing(self._override_db_connection.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM root WHERE identifier = ?;",
                (self.identifier,)
            )

            row = cursor.fetchone()

            if row is not None:
                self._is_override = True
                self._database_id = row[0]
                self.json_data = json.loads(row[2])

                self._settings = SettingsDatabaseEntry(user_db_connection, identifier)
                return

        # Empty populate
        self._database_id = None
        self.json_data = {}

    def exists(self):
        return self.database_id is not None or self.is_override

    @property
    def is_override(self):
        return self._is_override

    @property
    def database_id(self):
        return self._database_id

    @property
    def identifier(self):
        return self._identifier

    @property
    def override_settings(self):
        return self._settings

    def _insert(self):
        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO root (identifier, json) VALUES (?, ?);",
                (self._identifier, json.dumps(self.json_data), )
            )

            self._database_id = cursor.lastrowid

            self._user_db_connection.commit()

    def _update(self):
        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "UPDATE root SET json = ? WHERE id = ?;",
                (json.dumps(self.json_data), self._database_id, )
            )

            self._user_db_connection.commit()

    def save(self):
        if self._user_db_connection.closed:
            raise EnvironmentError(
                "User overrides database is closed, and we just tried to save {} to it".format(
                    self._identifier,
                )
            )

        # If there's no id, this is new
        if self._is_override or self._database_id is None:
            self._insert()
            self._is_override = False
        else:
            self._update()

    def delete(self):
        if self._user_db_connection.closed:
            raise EnvironmentError(
                "User overrides database is closed, and we just tried to delete {} from it".format(
                    self._identifier,
                )
            )

        # Nothing to do here
        if self._is_override or self._database_id is None:
            return

        with closing(self._user_db_connection.cursor()) as cursor:
            cursor.execute(
                "DELETE FROM root WHERE id = ?",
                (self._database_id, )
            )

            self._user_db_connection.commit()

        self._database_id = None
        self.json_data = {}


class UserDatabaseHelper(object):
    def __init__(self, system):
        if system is None:
            raise TypeError("System cannot be empty")

        self.system = system

        # Contains user configs
        self.user_db = os.path.join(
            CONFIGS_PATH,
            system,
            "user.db"
        )

        # Contains override configs
        self.override_db = os.path.join(
            CONFIGS_PATH,
            system,
            "override.db"
        )

        if os.path.isfile(self.override_db):
            self.override_db_connection = sqlite3.connect(self.override_db)
        else:
            self.override_db_connection = None

        # Why do we check if it exists first?, because opening a connection could create the file
        if not os.path.isfile(self.user_db):
            self.user_db_connection = sqlite3.connect(self.user_db)
            self._create_user_database()
        else:
            self.user_db_connection = sqlite3.connect(self.user_db)

    def _create_user_database(self):
        with closing(self.user_db_connection.cursor()) as cursor:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS root (
                        id INTEGER PRIMARY KEY,
                        identifier TEXT UNIQUE,
                        json TEXT
                    );
                ''')

            # Index for faster loading times
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_identifier ON root(identifier);"
            )

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY,
                        identifier TEXT UNIQUE,
                        ignored INTEGER,
                        asked INTEGER
                    );
                ''')

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_identifier ON settings(identifier);"
            )

            self.user_db_connection.commit()

    def fetch(self, identifier):
        return DatabaseEntry(self.user_db_connection, self.override_db_connection, identifier)

    def close(self):
        if hasattr(self, 'user_db_connection') and self.user_db_connection is not None:
            self.user_db_connection.close()

        if hasattr(self, 'override_db_connection') and self.override_db_connection is not None:
            self.override_db_connection.close()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            print("Couldn't destroy UserDatabaseHelper:", e)
