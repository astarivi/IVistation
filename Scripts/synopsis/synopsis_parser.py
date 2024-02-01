import os
import zlib
import sqlite3


def main(folder, database, crc_index=True):
    # Initialize target database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS root (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                xtrasname VARCHAR UNIQUE,
                synopsis BLOB
            );
        ''')

    if crc_index:
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS crc (
                    id INTEGER PRIMARY KEY,
                    crc VARCHAR UNIQUE,
                    root_id INTEGER
                );
            ''')

    conn.commit()

    current_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    synopsis_folder = os.path.join(current_folder, folder)
    total_count = len(os.listdir(synopsis_folder))
    count = 0

    insert_query = '''
            INSERT INTO root (name, xtrasname, synopsis) VALUES (?, ?, ?);
        '''

    for synopsis_file in os.listdir(synopsis_folder):
        count += 1
        print("{}/{}".format(count, total_count))

        full_synopsis_path = os.path.join(synopsis_folder, synopsis_file)
        xtrasname = os.path.splitext(synopsis_file)[0]

        with open(full_synopsis_path, 'rb') as synopsis_handle:
            first_line = synopsis_handle.readline().decode('utf-8')
            if not first_line.startswith("Name: "):
                continue
            # Read the first name, and remove "Name: " from the start, then strip any remaining blank characters.
            name = first_line[6:].strip()
            # Seek to start again
            synopsis_handle.seek(0)
            compressed_synopsis = zlib.compress(
                synopsis_handle.read(),
                9
            )

        print(name, xtrasname)

        cursor.execute(
            insert_query,
            (name, xtrasname, sqlite3.Binary(compressed_synopsis),)
        )

    conn.commit()

    if not crc_index:
        conn.close()
        print("Done!")
        return

    # First table done, now let's parse the indexes

    select_query = '''
            SELECT * FROM root WHERE xtrasname = ?;
        '''

    crc_insert_query = '''
            INSERT INTO crc (crc, root_id) VALUES (?, ?);
        '''

    with open("crcindex.txt", "r") as crc_index_handle:
        print("Creating indexes...")
        crc_indexes = []

        for line in crc_index_handle.readlines():
            # This is a header
            if ("[" in line and "]" in line) and ("Xtrasname" not in line):
                header_indexes = line.lower()

                # Clean it
                for char in "[] ":
                    header_indexes = header_indexes.replace(char, "")

                crc_indexes = header_indexes.split(",") if "," in header_indexes else [header_indexes]
                continue

            if "Xtrasname" not in line:
                continue

            if len(crc_indexes) == 0:
                continue

            xtras_name = line[10:].strip()

            # Look for the id
            cursor.execute(select_query, (xtras_name,))

            row = cursor.fetchone()

            # This won't be of any use to us.
            if row is None:
                continue

            for crc_val in crc_indexes:
                cursor.execute(
                    crc_insert_query,
                    (crc_val, row[0])
                )

        conn.commit()
        conn.close()
        print("Done!")


if __name__ == '__main__':
    main("in", "snes.db")
