import re
import zlib
import sqlite3
import xml.etree.ElementTree as ET
from collections import OrderedDict


TAGS_VERBOSE = OrderedDict([
    ("title", "Name"),
    ("developer", "Developer"),
    ("publisher", "Publisher"),
    ("features_general", "Features"),
    ("features_online", "Online Features"),
    ("genre", "Genre"),
    ("release_date", "Release Year"),
    ("rating", "Rating"),
    ("titleid", "Identifier")
])


def clean_thumbnail_name(name):
    """
    Subjects the filename to the exact same processing that would
    take place in IVistation. This is the name of the thumbnail,
    not the target filename.
    """
    pattern = re.compile(r'[(\[][^)\]]*[)\]]')
    return re.sub(pattern, '', name).strip()


def generate_synopsis(synopsis):
    line_format = u"{}: {}\n"
    result = u""

    for synopsis_tag, verbose_tag in TAGS_VERBOSE.items():
        value = synopsis.find(synopsis_tag).text

        # Skip empty key
        if value is None or value.strip() == "":
            continue

        result += line_format.format(verbose_tag, value)

    result += "_________________________\n"

    overview = synopsis.find("overview").text

    if overview is not None and overview.strip() != "":
        result += overview

    return result


def main(xml_files):
    # Initialize target database
    conn = sqlite3.connect("xbox.db")
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS root (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                xtrasname VARCHAR UNIQUE,
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

    insert_query = '''
            INSERT INTO root (name, xtrasname, synopsis) VALUES (?, ?, ?);
        '''

    xtras_names = []
    xtras_relation = {}

    for xml_file in xml_files:
        print("Processing " + xml_file)

        tree = ET.parse(xml_file)
        root = tree.getroot()

        for synopsis in root.findall('.//synopsis'):
            if synopsis.find("titleid").text is None:
                print("Skipping empty titleid")
                continue

            compressed_synopsis = zlib.compress(
                # Why? Because Python is dumb
                generate_synopsis(synopsis).encode("utf-8"),
                9
            )

            name = synopsis.find("title").text
            xtrasname = clean_thumbnail_name(synopsis.find("foldername").text)

            if xtrasname in xtras_names:
                print("Duplicated!: ", xtrasname)
                continue

            xtras_names.append(xtrasname)

            cursor.execute(
                insert_query,
                (clean_thumbnail_name(name), xtrasname, sqlite3.Binary(compressed_synopsis),)
            )

            xtras_relation[synopsis.find("titleid").text] = cursor.lastrowid

    conn.commit()

    # First table done, now let's parse the indexes
    crc_insert_query = '''
            INSERT INTO crc (crc, root_id) VALUES (?, ?);
        '''

    for titleid, root_id in xtras_relation.items():
        cursor.execute(
            crc_insert_query,
            (titleid, root_id,)
        )

    conn.commit()
    conn.close()
    print("Done!")


if __name__ == '__main__':
    main(["NTSC.xml", "PAL.xml", "JPN.xml"])
