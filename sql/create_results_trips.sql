DROP TABLE IF EXISTS results.trips;
CREATE TABLE IF NOT EXISTS results.trips (
    trip_id int,
	poi_type varchar,
	strata varchar,
    departure_time varchar,
    arrival_time varchar,
    total_time float,
    walk_time float,
    transfer_wait_time float,
    initial_wait_time float,
    transit_time float,
    walk_dist float,
    transit_dist float,
    total_dist float,
    num_transfers int,
    fare float
);

DROP INDEX if exists trip_id_idx;
CREATE INDEX if not exists trip_id_idx on results.trips(trip_id);
