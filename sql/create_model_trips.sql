DROP TABLE if exists model.trips;

CREATE TABLE model.trips AS (
    SELECT
        row_number() over () as trip_id,
        oa_id,
        poi_id,
		poi_type,
		stratum,
        date,
        time,
        0 AS computed
    FROM model.k_poi
    CROSS JOIN model.timestamps
);

ALTER TABLE model.trips ADD PRIMARY KEY (trip_id);

CREATE INDEX IF NOT EXISTS trip_id_idx on model.trips(trip_id);
CREATE INDEX IF NOT EXISTS oa_id_idx on model.trips(oa_id);
CREATE INDEX IF NOT EXISTS poi_id_idx on model.trips(poi_id);
