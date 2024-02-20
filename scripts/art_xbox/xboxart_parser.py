import os
import sqlite3
import zipfile
import argparse
import cloudinary
import cloudinary.uploader

INPUT_FOLDERS = [
    "NTSC",
    "PAL",
    "JPN",
    "Other"
]


def main():
    parser = argparse.ArgumentParser(description='Box art parser script.')
    parser.add_argument('--api-key', help='Cloudinary API key', dest='api_key', required=True)
    parser.add_argument('--api-secret', help='Cloudinary API key', dest='api_secret', required=True)

    args = parser.parse_args()

    api_key = args.api_key
    api_secret = args.api_secret

    current_folder = os.path.dirname(
        os.path.abspath(__file__)
    )

    output_folder = os.path.join(current_folder, "out")

    try:
        os.makedirs(output_folder)
    except:
        pass

    results = []

    for input_folder in INPUT_FOLDERS:
        working_path = os.path.join(current_folder, input_folder)

        for game_folder in [os.path.join(working_path, folder) for folder in os.listdir(working_path)]:
            details_file = os.path.join(game_folder, "detials.txt")
            resources_file = os.path.join(game_folder, "_resources.zip")

            if not os.path.isfile(details_file) or not os.path.isfile(resources_file):
                print("Folder {} is missing a required file.".format(game_folder))
                continue

            with open(details_file, "r") as details_handle:
                title_id = details_handle.read().split("|")[0].strip()

            target_file = os.path.join(output_folder, "{}.jpg".format(title_id))

            if os.path.isfile(target_file):
                print("Duplicated title id " + title_id)
                continue

            with zipfile.ZipFile(resources_file, 'r') as zip_ref:
                if "_resources/artwork/poster.jpg" not in zip_ref.namelist():
                    print("Image not found for " + game_folder)
                    continue

                with open(target_file, 'wb') as dest_file:
                    dest_file.write(zip_ref.read("_resources/artwork/poster.jpg"))

            results.append(
                [title_id, target_file]
            )

            print("Extracted image for " + title_id)

    c = raw_input("Processed {} entries. Press ENTER to continue uploading.".format(len(results)))

    conn = sqlite3.connect("xbox.db")
    cursor = conn.cursor()

    create_table_query = '''
                CREATE TABLE IF NOT EXISTS root (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    url TEXT
                );
            '''

    cursor.execute(create_table_query)

    index_query = '''
            CREATE INDEX IF NOT EXISTS idx_name ON root(name);
        '''

    cursor.execute(index_query)
    conn.commit()

    insert_query = '''
            INSERT INTO root (name, url) VALUES (?, ?);
        '''

    cloudinary.config(
        cloud_name="ddycuxdc0",
        api_key=api_key,
        api_secret=api_secret
    )

    total_count = len(results)
    current = 0

    for result in results:
        current += 1
        print("{}/{}".format(current, total_count))

        upload_result = cloudinary.uploader.upload(
            result[1],
            folder="xbox"
        )

        cursor.execute(
            insert_query,
            (result[0], upload_result["url"], )
        )

    conn.commit()
    conn.close()
    print("Done!")


if __name__ == '__main__':
    main()
