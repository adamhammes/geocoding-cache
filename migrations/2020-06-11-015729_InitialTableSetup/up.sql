-- Every query to the server will create an entry in this table, whether we were
-- able to successfully geocode the address or not.

-- If we are able to succesfully geocode the address, then we will create an
-- entry in the `GeocodeHit` table.
CREATE TABLE GeocodeQuery (
    Id INTEGER PRIMARY KEY,
    -- The exact text provided in the query.
    RawAddress TEXT NOT NULL UNIQUE,
    -- We're using sqlite3 for our database, which doesn't have a dedicated
    -- DATETIME type.
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE GeocodeHit (
    Id INTEGER PRIMARY KEY,
    GeocodeQueryId INTEGER NOT NULL UNIQUE REFERENCES GeocodeQuery(Id),
    FormattedAddress TEXT NOT NULL,
    Latitude REAL NOT NULL,
    Longitude REAL NOT NULL,
    PostalCode TEXT NOT NULL,
    StreetNumber TEXT,
    -- The name of the service used to geocode this entry
    QueryProvider TEXT NOT NULL,
    LastQueriedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE GeocodeMissType (
    Id INTEGER PRIMARY KEY,
    Code TEXT NOT NULL
);

INSERT INTO GeocodeMissType(Code)
VALUES
    ("RATE_LIMIT_EXCEEDED"),
    ("IMPRECISE_ADDRESS"),
    ("UNPARSEABLE_ADDRESS"),
    ("UNKNOWN_ERROR");

CREATE TABLE GeocodeMiss (
    Id INTEGER PRIMARY KEY,
    GeocodeQueryId INTEGER NOT NULL REFERENCES GeocodeQuery(Id),
    MissTypeId INTEGER NOT NULL REFERENCES GeocodeMissType(Id),
    LastQueriedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);