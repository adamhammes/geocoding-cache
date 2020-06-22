import sqlite3
import typing

from geocoding_cache.providers import GeocodeHit, GeocodeResult, GeocodeMiss

select_result = """
SELECT
  Latitude,
  Longitude,
  FormattedAddress,
  StreetNumber,
  PostalCode,
  QueryProvider,
  CASE WHEN geocodeMiss.Id IS NULL THEN 1 ELSE 0 END AS IsHit,
  geocodeMissType.Code as MissCode
FROM GeocodeQuery geocodeQuery
LEFT JOIN GeocodeHit geocodeHit
  ON geocodeQuery.Id = geocodeHit.GeocodeQueryId
LEFT JOIN GeocodeMiss geocodeMiss
  ON geocodeQuery.Id = geocodeMiss.GeocodeQueryId
LEFT JOIN GeocodeMissType geocodeMissType
  ON geocodeMissType.Id = geocodeMiss.MissTypeId
WHERE geocodeQuery.RawAddress = ?;
"""

select_address = """
SELECT * FROM GeocodeQuery
WHERE RawAddress = (?);
"""

insert_query = """
INSERT INTO GeocodeQuery(RawAddress)
VALUES (?)
"""

insert_hit = """
INSERT INTO GeocodeHit(
    GeocodeQueryId,
    FormattedAddress,
    Latitude,
    Longitude,
    StreetNumber,
    PostalCode,
    QueryProvider
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""

insert_miss = """
INSERT INTO GeocodeMiss (
    GeocodeQueryId,
    MissTypeId
) VALUES (
    ?,
    (SELECT Id FROM GeocodeMissType gmt WHERE gmt.Code = ?)
);
"""


def fetch_result(
    conn: sqlite3.Connection, raw_address: str
) -> typing.Optional[GeocodeResult]:
    cursor = conn.cursor()
    result = cursor.execute(select_result, (raw_address,)).fetchone()

    if result is None:
        return None

    cursor.close()

    if result["IsHit"]:
        return GeocodeHit(
            latitude=result["Latitude"],
            longitude=result["Longitude"],
            display_address=result["FormattedAddress"],
            street_number=result["StreetNumber"],
            postal_code=result["PostalCode"],
            provider=result["QueryProvider"],
        )
    else:
        return GeocodeMiss(result["MissCode"])


def store_result(conn: sqlite3.Connection, raw_address: str, result: GeocodeResult):
    cursor = conn.cursor()
    cursor.execute(select_address, (raw_address,))
    query_row = cursor.fetchone()

    query_id = None
    if query_row is None:
        cursor.execute(insert_query, (raw_address,))
        query_id = cursor.lastrowid
    else:
        query_id = query_row["Id"]

    if result.is_miss():
        cursor.execute(insert_miss, (query_id, result.value))
    else:
        cursor.execute(
            insert_hit,
            (
                query_id,
                result.display_address,
                result.latitude,
                result.longitude,
                result.street_number,
                result.postal_code,
                result.provider,
            ),
        )

    cursor.close()
