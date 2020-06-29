DROP TABLE otp_results_summary;
CREATE TABLE otp_results_summary AS
SELECT
    oa_id,
    poi_type,
    stratum,
    count(*) as num_trips,
    sum(total_time) as sum_journey_time,
    sum(walk_dist) as sum_walking_distance,
    sum(fare) as sum_fare,
    sum(generalised_cost) as sum_generalised_cost
FROM 
    (
        SELECT 
            a.*, 
            b.oa_id, 
            c.type AS poi_type, 
            d.stratum,
            ( ( 1.5 * (total_time + initial_wait_corrected)) - (0.5 * transit_time) + ((fare * 3600) / 6.7) + (10 * num_transfers) ) / 60 AS generalised_cost
        FROM 
            (select *, initial_wait_time - 3600 as initial_wait_corrected from otp_results) AS a 
            LEFT JOIN otp_trips AS b ON a.trip_id = b.trip_id 
            LEFT JOIN poi AS c ON b.poi_id = c.poi_id
            LEFT JOIN trip_strata AS d ON a.trip_id = d.trip_id
    ) AS results_full
GROUP BY 1,2,3;
