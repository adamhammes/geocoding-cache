import datetime
import sqlite3
import tempfile

import boto3


def backup_db(source: sqlite3.Connection):
    print("Backing up the database")
    s3_client = boto3.client("s3")

    day_of_month = datetime.datetime.today().day
    object_name = f"geocoding_cache/{day_of_month:02}.sqlite3"

    with tempfile.NamedTemporaryFile() as destination_file:
        dest = sqlite3.connect(destination_file.name)
        print("Making a copy of the database...")
        source.backup(dest)

        dest.close()

        print("Uploading to s3...")
        s3_client.upload_file(destination_file.name, "kijiji-apartments", object_name)
        print("...done")


