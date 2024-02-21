import re
import os
import zlib
import sqlite3

from contextlib import closing

SYSTEM_LIST = [
    "gba",
    "gbc",
    "gb"
]


def clean_thumbnail_name(name):
    """
    Subjects the filename to the exact same processing that would
    take place in IVistation. This is the name of the thumbnail,
    not the target filename.
    """
    pattern = re.compile(r'[(\[][^)\]]*[)\]]')
    return re.sub(pattern, '', name).strip()


def main():
    db_connections = {}

    # Initialize target database
    for sys_t in SYSTEM_LIST:
        conn = sqlite3.connect(sys_t + ".db")
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS root (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR,
                        xtrasname VARCHAR,
                        synopsis BLOB
                    );
                ''')

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS crc (
                        id INTEGER PRIMARY KEY,
                        crc VARCHAR UNIQUE,
                        root_id INTEGER
                    );
                ''')

            conn.commit()

        db_connections[sys_t] = conn

    current_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    synopsis_folder = os.path.join(current_folder, "synopsis")
    total_count = len(os.listdir(synopsis_folder))
    count = 0

    insert_query = '''
            INSERT INTO root (name, xtrasname, synopsis) VALUES (?, ?, ?);
        '''

    xtras_relation = {}

    for synopsis_file in os.listdir(synopsis_folder):
        count += 1
        print("{}/{}".format(count, total_count))

        full_synopsis_path = os.path.join(synopsis_folder, synopsis_file)
        filename = os.path.splitext(synopsis_file)[0]

        print(filename)
        with open(full_synopsis_path, 'rb') as synopsis_handle:
            first_line = synopsis_handle.readline().decode('utf-8', errors='ignore')
            if first_line.startswith("Name: "):
                name = first_line[6:].strip()
            else:
                name = first_line.strip()

            # Seek to start again
            synopsis_handle.seek(0)
            compressed_synopsis = zlib.compress(
                synopsis_handle.read(),
                9
            )

        if filename.startswith("GBA - "):
            connection = db_connections["gba"]
            xtrasname = filename.split("-", 1)[-1].strip()
        elif filename.startswith("GBC - "):
            connection = db_connections["gbc"]
            xtrasname = filename.split("-", 1)[-1].strip()
        else:
            connection = db_connections["gb"]
            xtrasname = filename

        with closing(connection.cursor()) as cursor:
            cursor.execute(
                insert_query,
                (clean_thumbnail_name(name), clean_thumbnail_name(xtrasname), sqlite3.Binary(compressed_synopsis),)
            )

            xtras_relation[filename] = cursor.lastrowid

    for conn in db_connections.values():
        conn.commit()

    # First table done, now let's parse the indexes
    crc_insert_query = '''
            INSERT INTO crc (crc, root_id) VALUES (?, ?);
        '''

    crc_values = []

    with open("crcindex.txt", "r") as crc_index_handle:
        print("Creating indexes...")
        crc_indexes = []

        for line in crc_index_handle.readlines():
            # This is a header
            if ("[" in line and "]" in line) and ("Xtrasname" not in line):
                header_indexes = line.lower()

                # Clean it
                for char in "[] \n":
                    header_indexes = header_indexes.replace(char, "")

                # Empty header
                if header_indexes.strip() == "":
                    crc_indexes = []
                    continue

                crc_indexes = header_indexes.split(",") if "," in header_indexes else [header_indexes]
                continue

            if "Xtrasname" not in line or len(crc_indexes) == 0:
                continue

            xtras_name = line[10:].strip()

            # Empty Xtrasname value
            if xtras_name == "":
                continue

            if xtras_name not in xtras_relation:
                continue

            row_id = xtras_relation[xtras_name]

            # This won't be of any use to us.
            if row_id is None:
                continue

            for crc_val in crc_indexes:
                crc_val = crc_val.lower()

                if len(crc_val) != 8:
                    print("Invalid CRC32: ", crc_val)
                    continue

                if crc_val in crc_values:
                    print("Duplicated CRC value: ", crc_val, xtras_name)
                    continue

                crc_values.append(crc_val)

                print("{} -> {}".format(crc_val, row_id))

                if xtras_name.startswith("GBA - "):
                    connection = db_connections["gba"]
                elif xtras_name.startswith("GBC - "):
                    connection = db_connections["gbc"]
                else:
                    connection = db_connections["gb"]

                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        crc_insert_query,
                        (crc_val, row_id)
                    )

        for conn in db_connections.values():
            conn.commit()
            conn.close()

        print("Done!")


if __name__ == '__main__':
    main()
