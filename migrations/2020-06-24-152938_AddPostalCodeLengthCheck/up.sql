-- After running the geocode cache on ~1000 addresses, I noticed that there were
-- postal codes in the form of 'A2B' that were being stored. Unfortunately,
-- these aren't sufficiently precise to show on the map and should rightfully be
-- stored in `GeocodeMiss`. This migration deletes the mistaken hits and then
-- adds a check constraint on `GeocodeHit.PostalCode` to enfornce a length == 7.

-- First, to delete the broken entries.
DELETE FROM GeocodeHit WHERE length(PostalCode) != 7;

-- Then, delete "dangling" rows from `GeocodeQuery`.
DELETE FROM GeocodeQuery
WHERE Id NOT IN (
    SELECT GeocodeQueryId FROM GeocodeMiss
    UNION
    SELECT GeocodeQueryId FROM GeocodeHit
);

-- Now, to add the check constraint. As sqlite3 doesn't support ADD CONSTRAINT
-- in ALTER TABLE statements, this will be done in four steps.

--   1. Create a new table with the same schema as `GeocodeHit` + our check constraint;
CREATE TABLE GeocodeHit_copy (
    Id INTEGER PRIMARY KEY,
    GeocodeQueryId INTEGER NOT NULL UNIQUE REFERENCES GeocodeQuery(Id),
    FormattedAddress TEXT NOT NULL,
    Latitude REAL NOT NULL,
    Longitude REAL NOT NULL,
    PostalCode TEXT NOT NULL,
    StreetNumber TEXT,
    -- The name of the service used to geocode this entry
    QueryProvider TEXT NOT NULL,
    LastQueriedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK(length(PostalCode = 7))
);

--   2. Insert all the rows from `GeocodeHit` into our new table;
INSERT INTO GeocodeHit_copy SELECT * FROM GeocodeHit;

--   3. Drop `GeocodeHit`;
DROP TABLE GeocodeHit;

--   4. Rename our copied table to `GeocodeHit`.
ALTER TABLE GeocodeHit_copy RENAME TO GeocodeHit;