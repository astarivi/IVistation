import re
import os
import zlib
import sqlite3


def clean_thumbnail_name(name):
    """
    Subjects the filename to the exact same processing that would
    take place in IVistation. This is the name of the thumbnail,
    not the target filename.
    """
    pattern = re.compile(r'[(\[][^)\]]*[)\]]')
    return re.sub(pattern, '', name).strip()


def main(folder, database, crc_index=True, no_leading_name_tag=False):
    # Initialize target database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS root (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                xtrasname VARCHAR,
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

    xtras_names = []
    xtras_relation = {}

    for synopsis_file in os.listdir(synopsis_folder):
        count += 1
        print("{}/{}".format(count, total_count))

        full_synopsis_path = os.path.join(synopsis_folder, synopsis_file)
        xtrasname = os.path.splitext(synopsis_file)[0]

        with open(full_synopsis_path, 'rb') as synopsis_handle:
            first_line = synopsis_handle.readline().decode('utf-8')
            if first_line.startswith("Name: "):
                name = first_line[6:].strip()
            else:
                if no_leading_name_tag:
                    name = first_line.strip()
                else:
                    continue

            # Read the first name, and remove "Name: " from the start, then strip any remaining blank characters.
            # Seek to start again
            synopsis_handle.seek(0)
            compressed_synopsis = zlib.compress(
                synopsis_handle.read(),
                9
            )

        if xtrasname in xtras_names:
            print("Duplicated!: ", xtrasname)
            continue

        xtras_names.append(xtrasname)

        cursor.execute(
            insert_query,
            (clean_thumbnail_name(name), clean_thumbnail_name(xtrasname), sqlite3.Binary(compressed_synopsis),)
        )

        xtras_relation[xtrasname] = cursor.lastrowid

    conn.commit()

    if not crc_index:
        conn.close()
        print("Done!")
        return

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

            if "Xtrasname" not in line:
                continue

            if len(crc_indexes) == 0:
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
                if crc_val in crc_values:
                    print("Duplicated CRC value: ", crc_val, xtras_name)
                    continue

                crc_values.append(crc_val)

                cursor.execute(
                    crc_insert_query,
                    (crc_val, row_id)
                )

        conn.commit()
        conn.close()
        print("Done!")


if __name__ == '__main__':
    main("in", "nes.db", no_leading_name_tag=True)
