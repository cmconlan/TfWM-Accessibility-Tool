SELECT
  pop.oa_id,
  access.average_gen_score / pop.pop_count AS at_risk_score
FROM (
    SELECT
      *
    FROM (
        SELECT
          oa_id,
          sum(count) AS pop_count
        FROM populations
        GROUP BY
          1
        ORDER BY
          pop_count DESC
      ) AS sub_pop
    LIMIT
      4231
  ) AS pop
LEFT JOIN (
    SELECT
      oa_id,
      sum(sum_gen_cost) / sum(num_trips) AS average_gen_score
    FROM otp_results_summary
    GROUP BY
      1
  ) AS access ON pop.oa_id = access.oa_id;