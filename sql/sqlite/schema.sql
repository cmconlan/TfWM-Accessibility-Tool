CREATE TABLE `trip_strata`
(
 `trip_id` bigint(20) NOT NULL DEFAULT '0' ,
 `stratum` text NULL ,
 `date`    text NULL ,
 `time`    text NULL ,

PRIMARY KEY (`trip_id`)
);
CREATE TABLE `poi`
(
 `poi_id`  int(11) NOT NULL DEFAULT '0' ,
 `type`    varchar(255) NULL DEFAULT NULL ,
 `name`    varchar(255) NULL DEFAULT NULL ,
 `poi_lat` double NULL DEFAULT NULL ,
 `poi_lon` double NULL DEFAULT NULL ,

PRIMARY KEY (`poi_id`)
);
CREATE TABLE `oa`
(
 `oa_id`                                            varchar(10) PRIMARY KEY,
 `oa_lat`                                           double NULL DEFAULT NULL ,
 `oa_lon`                                           double NULL DEFAULT NULL ,
 `year`                                             int(11) NULL DEFAULT NULL ,
 `age_all_residents`                                int(11) NULL DEFAULT NULL ,
 `age_0_to_5`                                       int(11) NULL DEFAULT NULL ,
 `age_5_to_7`                                       int(11) NULL DEFAULT NULL ,
 `age_8_to_9`                                       int(11) NULL DEFAULT NULL ,
 `age_10_to_14`                                     int(11) NULL DEFAULT NULL ,
 `age_15`                                           int(11) NULL DEFAULT NULL ,
 `age_16_to_17`                                     int(11) NULL DEFAULT NULL ,
 `age_18_to_19`                                     int(11) NULL DEFAULT NULL ,
 `age_20_to_24`                                     int(11) NULL DEFAULT NULL ,
 `age_25_to_29`                                     int(11) NULL DEFAULT NULL ,
 `age_30_to_44`                                     int(11) NULL DEFAULT NULL ,
 `age_45_to_59`                                     int(11) NULL DEFAULT NULL ,
 `age_60_to_64`                                     int(11) NULL DEFAULT NULL ,
 `age_65_to_74`                                     int(11) NULL DEFAULT NULL ,
 `age_75_to_84`                                     int(11) NULL DEFAULT NULL ,
 `age_85_to_89`                                     int(11) NULL DEFAULT NULL ,
 `age_90_plus`                                      int(11) NULL DEFAULT NULL ,
 `age_mean`                                         double NULL DEFAULT NULL ,
 `age_median`                                       double NULL DEFAULT NULL ,
 `cars_all_households`                              int(11) NULL DEFAULT NULL ,
 `cars_no_car`                                      int(11) NULL DEFAULT NULL ,
 `cars_1_car`                                       int(11) NULL DEFAULT NULL ,
 `cars_2_cars`                                      int(11) NULL DEFAULT NULL ,
 `cars_3_cars`                                      int(11) NULL DEFAULT NULL ,
 `cars_4_plus_cars`                                 int(11) NULL DEFAULT NULL ,
 `cars_sum_of_cars`                                 int(11) NULL DEFAULT NULL ,
 `rural_urban`                                      varchar(255) NULL DEFAULT NULL ,
 `disability_all`                                   int(11) NULL DEFAULT NULL ,
 `disability_severe`                                int(11) NULL DEFAULT NULL ,
 `disability_moderate`                              int(11) NULL DEFAULT NULL ,
 `disability_none`                                  int(11) NULL DEFAULT NULL ,
 `emp_all_residents_16_to_74`                       int(11) NULL DEFAULT NULL ,
 `emp_active`                                       int(11) NULL DEFAULT NULL ,
 `emp_active_in_employment`                         int(11) NULL DEFAULT NULL ,
 `emp_active_part_time`                             int(11) NULL DEFAULT NULL ,
 `emp_active_full_time`                             int(11) NULL DEFAULT NULL ,
 `emp_active_self_employed`                         int(11) NULL DEFAULT NULL ,
 `emp_active_unemployed`                            int(11) NULL DEFAULT NULL ,
 `emp_active_full_time_student`                     int(11) NULL DEFAULT NULL ,
 `emp_inactive`                                     int(11) NULL DEFAULT NULL ,
 `emp_inactive_retired`                             int(11) NULL DEFAULT NULL ,
 `emp_inactive_student`                             int(11) NULL DEFAULT NULL ,
 `emp_inactive_homemaking`                          int(11) NULL DEFAULT NULL ,
 `emp_inactive_disabled`                            int(11) NULL DEFAULT NULL ,
 `emp_inactive_other`                               int(11) NULL DEFAULT NULL ,
 `emp_unemployed_16_to_24`                          int(11) NULL DEFAULT NULL ,
 `emp_unemployed_50_to_74`                          int(11) NULL DEFAULT NULL ,
 `emp_unemployed_never_worked`                      int(11) NULL DEFAULT NULL ,
 `emp_unemployed_long_term_unemployed`              int(11) NULL DEFAULT NULL ,
 `grade_all`                                        int(11) NULL DEFAULT NULL ,
 `grade_ab`                                         int(11) NULL DEFAULT NULL ,
 `grade_c1`                                         int(11) NULL DEFAULT NULL ,
 `grade_c2`                                         int(11) NULL DEFAULT NULL ,
 `grade_de`                                         int(11) NULL DEFAULT NULL ,
 `birth_country_all`                                int(11) NULL DEFAULT NULL ,
 `birth_country_europe_total`                       int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_total`                    int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_england`                  int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_n_ireland`                int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_scotland`                 int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_wales`                    int(11) NULL DEFAULT NULL ,
 `birth_country_europe_uk_other`                    int(11) NULL DEFAULT NULL ,
 `birth_country_europe_channel_islands`             int(11) NULL DEFAULT NULL ,
 `birth_country_europe_ireland`                     int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_total`                 int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_total`              int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_germany`            int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_lithuania`          int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_poland`             int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_romania`            int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_eu_other`              int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_rest_total`            int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_rest_turkey`           int(11) NULL DEFAULT NULL ,
 `birth_country_europe_other_rest_other`            int(11) NULL DEFAULT NULL ,
 `birth_country_africa_total`                       int(11) NULL DEFAULT NULL ,
 `birth_country_africa_n`                           int(11) NULL DEFAULT NULL ,
 `birth_country_africa_cw_total`                    int(11) NULL DEFAULT NULL ,
 `birth_country_africa_cw_nigeria`                  int(11) NULL DEFAULT NULL ,
 `birth_country_africa_cw_other`                    int(11) NULL DEFAULT NULL ,
 `birth_country_africa_se_total`                    int(11) NULL DEFAULT NULL ,
 `birth_country_africa_se_kenya`                    int(11) NULL DEFAULT NULL ,
 `birth_country_africa_se_south_africa`             int(11) NULL DEFAULT NULL ,
 `birth_country_africa_se_zimbabwe`                 int(11) NULL DEFAULT NULL ,
 `birth_country_africa_se_other`                    int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_total`                 int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_mideast_total`         int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_mideast_iran`          int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_mideast_other`         int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_east_asia_total`       int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_east_asia_china`       int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_east_asia_hong_kong`   int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_east_asia_other`       int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_south_asia_total`      int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_south_asia_bangladesh` int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_south_asia_india`      int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_south_asia_pakistan`   int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_south_asia_other`      int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_se_asia_total`         int(11) NULL DEFAULT NULL ,
 `birth_country_mideast_asia_central_asia_total`    int(11) NULL DEFAULT NULL ,
 `birth_country_americas_total`                     int(11) NULL DEFAULT NULL ,
 `birth_country_americas_north_america_total`       int(11) NULL DEFAULT NULL ,
 `birth_country_americas_north_america_caribbean`   int(11) NULL DEFAULT NULL ,
 `birth_country_americas_north_america_usa`         int(11) NULL DEFAULT NULL ,
 `birth_country_americas_north_america_other`       int(11) NULL DEFAULT NULL ,
 `birth_country_americas_central_america`           int(11) NULL DEFAULT NULL ,
 `birth_country_americas_south_america`             int(11) NULL DEFAULT NULL ,
 `birth_country_antarctica_oceania_total`           int(11) NULL DEFAULT NULL ,
 `birth_country_antarctica_oceania_australia`       int(11) NULL DEFAULT NULL ,
 `birth_country_antarctica_oceania_other`           int(11) NULL DEFAULT NULL ,
 `birth_country_other`                              int(11) NULL DEFAULT NULL ,
 `deprived_rural_urban`                             varchar(255) NULL DEFAULT NULL ,
 `deprived_all`                                     int(11) NULL DEFAULT NULL ,
 `deprived_0_dim`                                   int(11) NULL DEFAULT NULL ,
 `deprived_1_dim`                                   int(11) NULL DEFAULT NULL ,
 `deprived_2_dim`                                   int(11) NULL DEFAULT NULL ,
 `deprived_3_dim`                                   int(11) NULL DEFAULT NULL ,
 `deprived_4_dim`                                   int(11) NULL DEFAULT NULL ,
 `eng_prof_rural_urban`                             varchar(255) NULL DEFAULT NULL ,
 `eng_prof_all`                                     int(11) NULL DEFAULT NULL ,
 `eng_prof_main_english`                            int(11) NULL DEFAULT NULL ,
 `eng_prof_main_not_english_very_well`              int(11) NULL DEFAULT NULL ,
 `eng_prof_main_not_english_not_well`               int(11) NULL DEFAULT NULL ,
 `eng_prof_main_not_english_cannot`                 int(11) NULL DEFAULT NULL ,
 `eth_all`                                          int(11) NULL DEFAULT NULL ,
 `eth_white`                                        int(11) NULL DEFAULT NULL ,
 `eth_gypsy`                                        int(11) NULL DEFAULT NULL ,
 `eth_mixed`                                        int(11) NULL DEFAULT NULL ,
 `eth_asian_indian`                                 int(11) NULL DEFAULT NULL ,
 `eth_asian_pakistani`                              int(11) NULL DEFAULT NULL ,
 `eth_asian_bangladeshi`                            int(11) NULL DEFAULT NULL ,
 `eth_asian_chinese`                                int(11) NULL DEFAULT NULL ,
 `eth_asian_other`                                  int(11) NULL DEFAULT NULL ,
 `eth_black`                                        int(11) NULL DEFAULT NULL ,
 `eth_other`                                        int(11) NULL DEFAULT NULL ,
 `lone_parent_total`                                int(11) NULL DEFAULT NULL ,
 `lone_parent_part_time_emp`                        int(11) NULL DEFAULT NULL ,
 `lone_parent_full_time_emp`                        int(11) NULL DEFAULT NULL ,
 `lone_parent_no_emp`                               int(11) NULL DEFAULT NULL ,
 `lone_parent_total_male`                           int(11) NULL DEFAULT NULL ,
 `lone_parent_part_time_emp_male`                   int(11) NULL DEFAULT NULL ,
 `lone_parent_full_time_emp_male`                   int(11) NULL DEFAULT NULL ,
 `lone_parent_no_emp_male`                          int(11) NULL DEFAULT NULL ,
 `lone_parent_total_female`                         int(11) NULL DEFAULT NULL ,
 `lone_parent_part_time_emp_female`                 int(11) NULL DEFAULT NULL ,
 `lone_parent_full_time_emp_female`                 int(11) NULL DEFAULT NULL ,
 `lone_parent_no_emp_female`                        int(11) NULL DEFAULT NULL ,
 `students_highest_qual_all`                        int(11) NULL DEFAULT NULL ,
 `students_no_qual`                                 int(11) NULL DEFAULT NULL ,
 `students_highest_qual_level_1`                    int(11) NULL DEFAULT NULL ,
 `students_highest_qual_level_2`                    int(11) NULL DEFAULT NULL ,
 `students_highest_qual_apprenticeship`             int(11) NULL DEFAULT NULL ,
 `students_highest_qual_level_3`                    int(11) NULL DEFAULT NULL ,
 `students_highest_qual_level_4_above`              int(11) NULL DEFAULT NULL ,
 `students_highest_qual_other`                      int(11) NULL DEFAULT NULL ,
 `students_16_to_17`                                int(11) NULL DEFAULT NULL ,
 `students_18_plus`                                 int(11) NULL DEFAULT NULL ,
 `students_employed`                                int(11) NULL DEFAULT NULL ,
 `students_unemployed`                              int(11) NULL DEFAULT NULL ,
 `students_econ_inactive`                           int(11) NULL DEFAULT NULL ,
 `usual_residents_all`                              int(11) NULL DEFAULT NULL ,
 `usual_residents_males`                            int(11) NULL DEFAULT NULL ,
 `usual_residents_females`                          int(11) NULL DEFAULT NULL ,
 `usual_residents_lives_in_household`               int(11) NULL DEFAULT NULL ,
 `usual_residents_lives_in_communal_establishment`  int(11) NULL DEFAULT NULL ,
 `usual_residents_student`                          int(11) NULL DEFAULT NULL ,
 `usual_residents_area_hectares`                    double NULL DEFAULT NULL ,
 `usual_residents_density_persons_per_hectare`      double NULL DEFAULT NULL ,
 `lsoa11`                                           varchar(255) NULL DEFAULT NULL

);
CREATE TABLE `otp_trips`
(
 `oa_id`   varchar(10) NOT NULL ,
 `poi_id`  int(11) NOT NULL DEFAULT '0' ,
 `date`    text NULL ,
 `time`    text NULL ,
 `trip_id` bigint(20) PRIMARY KEY ,
 `oa_lat`  double NULL DEFAULT NULL ,
 `oa_lon`  double NULL DEFAULT NULL ,
 `poi_lat` double NULL DEFAULT NULL ,
 `poi_lon` double NULL DEFAULT NULL ,
CONSTRAINT `otp_trips_ibfk_3 `FOREIGN KEY (`oa_id`) REFERENCES `oa` (`oa_id`),
CONSTRAINT `otp_trips_ibfk_2` FOREIGN KEY (`trip_id`) REFERENCES `trip_strata` (`trip_id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `otp_trips_ibfk_4` FOREIGN KEY (`poi_id`) REFERENCES `poi` (`poi_id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE `otp_results`
(
 `trip_id`            bigint(20) PRIMARY KEY,
 `departure_time`     text NULL DEFAULT NULL ,
 `arrival_time`       text NULL DEFAULT NULL ,
 `total_time`         double NULL DEFAULT NULL ,
 `walk_time`          double NULL DEFAULT NULL ,
 `transfer_wait_time` double NULL DEFAULT NULL ,
 `initial_wait_time`  double NULL DEFAULT NULL ,
 `transit_time`       double NULL DEFAULT NULL ,
 `walk_dist`          double NULL DEFAULT NULL ,
 `transit_dist`       double NULL DEFAULT NULL ,
 `total_dist`         double NULL DEFAULT NULL ,
 `num_transfers`      int(11) NULL DEFAULT NULL ,
 `fare`               text NULL ,
CONSTRAINT `otp_results_ibfk_1` FOREIGN KEY (`trip_id`) REFERENCES `trip_strata` (`trip_id`)
);
CREATE TABLE populations(oa_id varchar(10), population text, count integer);
CREATE TABLE otp_results_summary(
  oa_id TEXT,
  poi_type TEXT,
  stratum TEXT,
  num_trips,
  sum_journey_time,
  sum_walking_distance,
  sum_fare,
  sum_generalised_cost
);
