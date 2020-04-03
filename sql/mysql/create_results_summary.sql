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
            (total_time*1.5) + ((initial_wait_time + transfer_wait_time) * 1.5) + ((total_time - walk_time) * 1.5) + (num_transfers * 10) + (fare / 6.7) AS generalised_cost
        FROM 
            otp_results AS a 
            LEFT JOIN otp_trips AS b ON a.trip_id = b.trip_id 
            LEFT JOIN poi AS c ON b.poi_id = c.poi_id
            LEFT JOIN trip_strata AS d ON a.trip_id = d.trip_id
    ) AS results_full
GROUP BY 1,2,3;