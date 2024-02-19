import sqlite3

DATA = [
    ["49470074", "Forgotten Realms: Demon Stone"],
    ["4541000E", "Harry Potter and the Chamber of Secrets"],
    ["4541007B", "Need for Speed Most Wanted"],
    ["4D440004", "Stake: Fortune Fighters"],
    ["54510028", "The Incredibles"],
    ["45410043", "The Sims: Bustin' Out"],
    ["4B4E001E", "Yu-Gi-Oh! The Dawn of Destiny (PAL)"]
]


def main():
    # Initialize target database
    conn = sqlite3.connect("xbox.db")
    cursor = conn.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS root (
            id INTEGER PRIMARY KEY,
            crc TEXT UNIQUE,
            title TEXT
        );
    '''

    cursor.execute(create_table_query)

    index_query = '''
        CREATE INDEX IF NOT EXISTS idx_crc ON root(crc);
    '''

    cursor.execute(index_query)

    conn.commit()

    insert_query = '''
        INSERT INTO root (crc, title) VALUES (?, ?);
    '''

    for row in DATA:
        cursor.execute(insert_query, row)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
