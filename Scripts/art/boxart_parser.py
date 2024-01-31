"""
This is a tiny tool to process box art (or equivalent thumbnails) for games.

Given a Cloudinary API key, and an input folder populated with correctly
named art (following the no-intro dat-o-matic convention), outputs a
database containing the name of the boxart related to the remote
URL containing the image.

Requires Python 3 and Pillow, as the image may undergo compression to
optimize storage space.

Keep in mind, the images placed in the input directory will be modified, so
make sure they're a copy of your collection.
"""

import re
import os
import sqlite3
import argparse
import cloudinary
import cloudinary.uploader
from PIL import Image


def clean_thumbnail_name(name):
    """
    Subjects the filename to the exact same processing that would
    take place in IVistation. This is the name of the thumbnail,
    not the target filename.
    """
    name = name.replace("'", "_")
    pattern = re.compile(r'\([^)]*\)')
    return re.sub(pattern, '', name).strip()


def process_images(images_folder):
    print("Converting files...")
    for image in os.listdir(images_folder):
        if image.endswith(".jpg"):
            continue

        image_path = os.path.join(images_folder, image)
        destination = os.path.join(
            images_folder,
            image[:-3] + "jpg"
        )

        if os.path.isfile(destination):
            continue

        with Image.open(image_path) as image_file:
            if image_file.mode != "RGB":
                image_file = image_file.convert("RGB")

            image_file.save(destination, quality=90)

        # Remove the OG file
        os.remove(image_path)


def main():
    # Parse args
    parser = argparse.ArgumentParser(description='Box art parser script.')
    parser.add_argument('--api-key', help='Cloudinary API key', dest='api_key', required=True)
    parser.add_argument('--api-secret', help='Cloudinary API key', dest='api_secret', required=True)
    parser.add_argument('--input-folder', help='Input folder', dest='input_folder', required=True)
    parser.add_argument('--output', help='Output database file', dest='output', required=True)

    args = parser.parse_args()

    api_key = args.api_key
    api_secret = args.api_secret
    input_folder = args.input_folder
    output = args.output

    # Get paths
    current_folder = os.path.dirname(
        os.path.abspath(__file__)
    )
    images_folder = os.path.join(current_folder, input_folder)

    # Process the images. This will convert them to 90% quality JPGs with an RGB colorspace
    process_images(images_folder)

    # Upload the images
    cloudinary.config(
        cloud_name="ddycuxdc0",
        api_key=api_key,
        api_secret=api_secret
    )

    data = []
    count = 0
    # The longest element for any of these. Used later in the sqlite database.
    max_lengths = [-1, -1]
    potential_files = os.listdir(images_folder)

    for image in potential_files:
        count += 1
        if not image.endswith(".jpg"):
            continue

        thumbnail_name = clean_thumbnail_name(image[:-4])

        # Remove duplicates
        if any(thumbnail_name == subarray[0] for subarray in data):
            print("Found duplicate: ", thumbnail_name)
            continue

        image_path = os.path.join(images_folder, image)

        upload_result = cloudinary.uploader.upload(
            image_path,
            folder=output[:-3]
        )

        upload_url = upload_result["url"]

        data.append(
            (thumbnail_name, upload_url)
        )

        print("{}/{}".format(count, len(potential_files)))

        max_lengths[0] = max(len(thumbnail_name), max_lengths[0])
        max_lengths[1] = max(len(upload_url), max_lengths[1])

    # Prepare the database
    print("Committing to database...")
    conn = sqlite3.connect(output)
    cursor = conn.cursor()

    create_table_query = '''
            CREATE TABLE IF NOT EXISTS root (
                id INTEGER PRIMARY KEY,
                name VARCHAR({}) UNIQUE,
                url VARCHAR({})
            );
        '''.format(max_lengths[0] + 1, max_lengths[1] + 1)

    cursor.execute(create_table_query)

    index_query = '''
        CREATE INDEX IF NOT EXISTS idx_name ON root(name);
    '''

    cursor.execute(index_query)
    conn.commit()

    insert_query = '''
        INSERT INTO root (name, url) VALUES (?, ?);
    '''

    for row in data:
        cursor.execute(insert_query, row)

    conn.commit()
    conn.close()
    print("Done!")


if __name__ == '__main__':
    main()
