import os
import sqlite3
import urllib.request

import dotenv
from flask import current_app, Flask, g, request
import requests

import geocoding_cache.db
import geocoding_cache.providers

app = Flask(__name__)


def get_provider():
    if "_provider" not in g:
        g._provider = current_app.config.get(
            "GEOCODING_PROVIDER", geocoding_cache.providers.google
        )

    return g._provider


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_url = current_app.config.get("DATABASE_URL")
        if db_url is None:
            db_url = os.environ["DATABASE_URL"]

        g.db = db = sqlite3.connect(db_url)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")

    return g.db


@app.route("/")
def hello():
    raw_address = request.args.get("address")

    if raw_address is None:
        return {"status": "BAD_REQUEST", "result": None}, 400

    connection = get_db()

    geocode_result = geocoding_cache.db.fetch_result(connection, raw_address)
    if geocode_result is None:
        geocode_result = get_provider()(raw_address)
        geocoding_cache.db.store_result(connection, raw_address, geocode_result)

    connection.commit()

    if geocode_result.is_miss():
        return {"status": geocode_result.value, "result": None}
    else:
        return {"status": "OK", "result": geocode_result._asdict()}


@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()
