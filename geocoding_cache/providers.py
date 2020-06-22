import enum
import os
import typing
import urllib.request

import requests


class GeocodeMiss(enum.Enum):
    RateLimitExceeded = "RATE_LIMIT_EXCEEDED"
    ImpreciseAddress = "IMPRECISE_ADDRESS"
    UnparseableAddress = "UNPARSEABLE_ADDRESS"
    UnknownError = "UNKNOWN_ERROR"

    def is_miss(self) -> bool:
        return True


class GeocodeHit(typing.NamedTuple):
    latitude: float
    longitude: float
    display_address: str
    street_number: str
    postal_code: str
    provider: str

    def is_miss(self) -> bool:
        return False


GeocodeResult = typing.Union[GeocodeMiss, GeocodeHit]


def geocod(address: str):
    return requests.get(
        "https://api.geocod.io/v1.6/geocode",
        params={"q": address, "api_key": geocod_api_key, "country": "Canada"},
    ).content


def mapbox(address: str):
    encoded_address = urllib.request.pathname2url(address)
    return requests.get(
        f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}",
        params={"access_token": mapbox_api_key},
    ).content


def nominatim(address: str):
    return requests.get(
        "https://nominatim.openstreetmap.org/search/",
        params={"q": address, "addressdetails": "1", "format": "json"},
    ).content


def google(address: str) -> GeocodeResult:
    google_api_key = os.environ["GOOGLE_API_KEY"]

    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": address, "key": google_api_key},
    ).json()

    if response["status"] == "OVER_QUERY_LIMIT":
        return GeocodeMiss.RateLimitExceeded

    if response["status"] == "ZERO_RESULTS":
        return GeocodeMiss.UnparseableAddress

    if response["status"] != "OK":
        return GeocodeMiss.UnknownError

    result = response["results"][0]
    geometry = result["geometry"]

    if geometry["location_type"] != "ROOFTOP":
        return GeocodeMiss.ImpreciseAddress

    street_number, postal_code = None, None
    for address_part in result["address_components"]:
        if "street_number" in address_part["types"]:
            street_number = address_part["long_name"]

        if "postal_code" in address_part["types"]:
            postal_code = address_part["long_name"]

    if street_number is None or postal_code is None:
        return GeocodeMiss.ImpreciseAddress

    return GeocodeHit(
        latitude=geometry["location"]["lat"],
        longitude=geometry["location"]["lng"],
        display_address=result["formatted_address"],
        street_number=street_number,
        postal_code=postal_code,
        provider="google",
    )
