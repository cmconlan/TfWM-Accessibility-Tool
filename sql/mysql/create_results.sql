CREATE TABLE IF NOT EXISTS trip_results (
    trip_id int PRIMARY KEY,
    departure_time text,
    arrival_time text,
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