import datetime
import io
import sqlite3
import tempfile

import boto3


def backup_db(source: sqlite3.Connection):
    print("Backing up the database")
    with tempfile.NamedTemporaryFile() as destination_file:
        dest = sqlite3.connect(destination_file.name)
        print("Making a copy of the database...")
        source.backup(dest)

        dest.close()

        in_memory_db = io.BytesIO(destination_file.read())

    s3_client = boto3.client("s3")

    day_of_week = datetime.datetime.today().weekday()
    object_name = f"geocoding_cache/{day_of_week}.sqlite3"

    print("Uploading to s3...")
    s3_client.upload_fileobj(in_memory_db, "kijiji-apartments", object_name)
    print("...done")
