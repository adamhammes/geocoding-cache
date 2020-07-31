import glob
import json
import os
import tempfile
import unittest.mock

import dotenv
import pytest

from geocoding_cache import server
from geocoding_cache.providers import GeocodeHit, GeocodeMiss


@pytest.fixture
def provider():
    return unittest.mock.Mock()


@pytest.fixture
def client(provider):
    db_fd, server.app.config["DATABASE_URL"] = tempfile.mkstemp()
    server.app.config["GEOCODING_PROVIDER"] = provider
    server.app.config["TESTING"] = True

    with server.app.test_client() as client:
        with server.app.app_context():
            db = server.get_db()

            migration_files = sorted(glob.glob("migrations/**/up.sql"))
            for migration_file in migration_files:
                with open(migration_file) as migration_content:
                    db.executescript(migration_content.read())

        yield client

    os.close(db_fd)
    os.unlink(server.app.config["DATABASE_URL"])


def test_returns_bad_request_on_missing_address(client, provider):
    response = client.get("/")
    assert response.status_code == 400


def test_miss(client, provider):
    provider.return_value = GeocodeMiss.ImpreciseAddress
    address_query = "Quebec City, Québec, Canada"
    expected_result = {
        "result": None,
        "status": GeocodeMiss.ImpreciseAddress.value,
        "cache_type": "MISS",
    }

    response = client.get("/", query_string={"address": address_query})
    provider.assert_called_once_with(address_query)
    assert response.status_code == 200

    result = json.loads(response.data)
    assert result == expected_result

    cached_response = client.get("/", query_string={"address": address_query})
    assert provider.not_called()

    cached_result = json.loads(cached_response.data)
    assert cached_result == {
        "result": None,
        "status": GeocodeMiss.ImpreciseAddress.value,
        "cache_type": "HIT",
    }


def test_hit(client, provider):
    query = "123 fake address"
    hit = GeocodeHit(
        latitude=40,
        longitude=40,
        display_address="Hello, world",
        street_number="123",
        postal_code="G1K 3S6",
        provider="mock",
    )

    provider.return_value = hit
    expected_result = {"status": "OK", "result": hit._asdict(), "cache_type": "MISS"}

    response = client.get("/", query_string={"address": query})
    provider.assert_called_once_with(query)
    assert response.status_code == 200

    result = json.loads(response.data)
    assert result == expected_result

    cached_response = client.get("/", query_string={"address": query})
    provider.not_called
    assert cached_response.status_code == 200

    result = json.loads(cached_response.data)
    assert result == {**expected_result, "cache_type": "HIT"}
