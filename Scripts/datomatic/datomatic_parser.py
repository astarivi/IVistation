import sqlite3
import xml.etree.ElementTree as ElementTree


def main(file):
    root = ElementTree.parse(file).getroot()

    biggest_title_name = 0

    data = []

    for game in root.findall('.//game'):
        game_name = game.attrib["name"]

        if "BIOS" in game_name:
            continue

        crc = game.find(".//rom").attrib["crc"]

        current_title_len = len(game_name)

        if current_title_len > biggest_title_name:
            biggest_title_name = current_title_len

        print(game_name, crc)

        data.append(
            (crc, game_name)
        )

    print(biggest_title_name)

    # Initialize target database
    conn = sqlite3.connect(file.split(".")[0] + ".db")
    cursor = conn.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS root (
            id INTEGER PRIMARY KEY,
            crc VARCHAR(8) UNIQUE,
            title VARCHAR({})
        );
    '''.format(biggest_title_name+1)

    cursor.execute(create_table_query)

    index_query = '''
        CREATE INDEX IF NOT EXISTS idx_crc ON root(crc);
    '''

    cursor.execute(index_query)

    conn.commit()

    insert_query = '''
        INSERT INTO root (crc, title) VALUES (?, ?);
    '''

    for row in data:
        cursor.execute(insert_query, row)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main("snes.dat")
