--
-- PostgreSQL database dump
--

-- Dumped from database version 10.12
-- Dumped by pg_dump version 10.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: semantic; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA semantic;


ALTER SCHEMA semantic OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: oa; Type: TABLE; Schema: semantic; Owner: postgres
--

CREATE TABLE semantic.oa (
    oa11 character varying NOT NULL,
    geometry public.geometry(MultiPolygon,4326),
    centroid public.geometry(Point,4326),
    snapped_centroid public.geometry,
    snapped_latitude double precision,
    snapped_longitude double precision,
    year integer,
    geography character varying,
    age_all_residents integer,
    age_0_to_5 integer,
    age_5_to_7 integer,
    age_8_to_9 integer,
    age_10_to_14 integer,
    age_15 integer,
    age_16_to_17 integer,
    age_18_to_19 integer,
    age_20_to_24 integer,
    age_25_to_29 integer,
    age_30_to_44 integer,
    age_45_to_59 integer,
    age_60_to_64 integer,
    age_65_to_74 integer,
    age_75_to_84 integer,
    age_85_to_89 integer,
    age_90_plus integer,
    age_mean double precision,
    age_median double precision,
    cars_all_households integer,
    cars_no_car integer,
    cars_1_car integer,
    cars_2_cars character varying,
    cars_3_cars integer,
    cars_4_plus_cars integer,
    cars_sum_of_cars integer,
    rural_urban character varying,
    disability_all integer,
    disability_severe integer,
    disability_moderate integer,
    disability_none integer,
    emp_all_residents_16_to_74 integer,
    emp_active integer,
    emp_active_in_employment integer,
    emp_active_part_time integer,
    emp_active_full_time integer,
    emp_active_self_employed integer,
    emp_active_unemployed integer,
    emp_active_full_time_student integer,
    emp_inactive integer,
    emp_inactive_retired integer,
    emp_inactive_student integer,
    emp_inactive_homemaking integer,
    emp_inactive_disabled integer,
    emp_inactive_other integer,
    emp_unemployed_16_to_24 integer,
    emp_unemployed_50_to_74 integer,
    emp_unemployed_never_worked integer,
    emp_unemployed_long_term_unemployed integer,
    grade_all integer,
    grade_ab integer,
    grade_c1 integer,
    grade_c2 integer,
    grade_de integer,
    birth_country_all integer,
    birth_country_europe_total integer,
    birth_country_europe_uk_total integer,
    birth_country_europe_uk_england integer,
    birth_country_europe_uk_n_ireland integer,
    birth_country_europe_uk_scotland integer,
    birth_country_europe_uk_wales integer,
    birth_country_europe_uk_other integer,
    birth_country_europe_channel_islands integer,
    birth_country_europe_ireland integer,
    birth_country_europe_other_total integer,
    birth_country_europe_other_eu_total integer,
    birth_country_europe_other_eu_germany integer,
    birth_country_europe_other_eu_lithuania integer,
    birth_country_europe_other_eu_poland integer,
    birth_country_europe_other_eu_romania integer,
    birth_country_europe_other_eu_other integer,
    birth_country_europe_other_rest_total integer,
    birth_country_europe_other_rest_turkey integer,
    birth_country_europe_other_rest_other integer,
    birth_country_africa_total integer,
    birth_country_africa_n integer,
    birth_country_africa_cw_total integer,
    birth_country_africa_cw_nigeria integer,
    birth_country_africa_cw_other integer,
    birth_country_africa_se_total integer,
    birth_country_africa_se_kenya integer,
    birth_country_africa_se_south_africa integer,
    birth_country_africa_se_zimbabwe integer,
    birth_country_africa_se_other integer,
    birth_country_mideast_asia_total integer,
    birth_country_mideast_asia_mideast_total integer,
    birth_country_mideast_asia_mideast_iran integer,
    birth_country_mideast_asia_mideast_other integer,
    birth_country_mideast_asia_east_asia_total integer,
    birth_country_mideast_asia_east_asia_china integer,
    birth_country_mideast_asia_east_asia_hong_kong integer,
    birth_country_mideast_asia_east_asia_other integer,
    birth_country_mideast_asia_south_asia_total integer,
    birth_country_mideast_asia_south_asia_bangladesh integer,
    birth_country_mideast_asia_south_asia_india integer,
    birth_country_mideast_asia_south_asia_pakistan integer,
    birth_country_mideast_asia_south_asia_other integer,
    birth_country_mideast_asia_se_asia_total integer,
    birth_country_mideast_asia_central_asia_total integer,
    birth_country_americas_total integer,
    birth_country_americas_north_america_total integer,
    birth_country_americas_north_america_caribbean integer,
    birth_country_americas_north_america_usa integer,
    birth_country_americas_north_america_other integer,
    birth_country_americas_central_america integer,
    birth_country_americas_south_america integer,
    birth_country_antarctica_oceania_total integer,
    birth_country_antarctica_oceania_australia integer,
    birth_country_antarctica_oceania_other integer,
    birth_country_other integer,
    deprived_rural_urban character varying,
    deprived_all integer,
    deprived_0_dim integer,
    deprived_1_dim integer,
    deprived_2_dim integer,
    deprived_3_dim integer,
    deprived_4_dim integer,
    eng_prof_rural_urban character varying,
    eng_prof_all integer,
    eng_prof_main_english integer,
    eng_prof_main_not_english_very_well integer,
    eng_prof_main_not_english_not_well integer,
    eng_prof_main_not_english_cannot integer,
    eth_all integer,
    eth_white integer,
    eth_gypsy integer,
    eth_mixed integer,
    eth_asian_indian integer,
    eth_asian_pakistani integer,
    eth_asian_bangladeshi integer,
    eth_asian_chinese integer,
    eth_asian_other integer,
    eth_black integer,
    eth_other integer,
    lone_parent_total integer,
    lone_parent_part_time_emp integer,
    lone_parent_full_time_emp integer,
    lone_parent_no_emp integer,
    lone_parent_total_male integer,
    lone_parent_part_time_emp_male integer,
    lone_parent_full_time_emp_male integer,
    lone_parent_no_emp_male integer,
    lone_parent_total_female integer,
    lone_parent_part_time_emp_female integer,
    lone_parent_full_time_emp_female integer,
    lone_parent_no_emp_female integer,
    students_highest_qual_all integer,
    students_no_qual integer,
    students_highest_qual_level_1 integer,
    students_highest_qual_level_2 integer,
    students_highest_qual_apprenticeship integer,
    students_highest_qual_level_3 integer,
    students_highest_qual_level_4_above integer,
    students_highest_qual_other integer,
    students_16_to_17 integer,
    students_18_plus integer,
    students_employed integer,
    students_unemployed integer,
    students_econ_inactive integer,
    usual_residents_all integer,
    usual_residents_males integer,
    usual_residents_females integer,
    usual_residents_lives_in_household integer,
    usual_residents_lives_in_communal_establishment integer,
    usual_residents_student integer,
    usual_residents_area_hectares double precision,
    usual_residents_density_persons_per_hectare double precision,
    lsoa11 character varying
);


ALTER TABLE semantic.oa OWNER TO postgres;

--
-- Name: pcd; Type: TABLE; Schema: semantic; Owner: postgres
--

CREATE TABLE semantic.pcd (
    pcd text NOT NULL,
    oa11 character varying,
    lsoa11 character varying,
    msoa11 character varying,
    centroid public.geometry(Point,4326),
    lon double precision,
    lat double precision,
    cty16nm character varying
);


ALTER TABLE semantic.pcd OWNER TO postgres;

--
-- Name: poi; Type: TABLE; Schema: semantic; Owner: postgres
--

CREATE TABLE semantic.poi (
    type character varying,
    name character varying,
    snapped_latitude double precision,
    snapped_longitude double precision,
    snapped_location public.geometry(Point,4326),
    id integer NOT NULL
);


ALTER TABLE semantic.poi OWNER TO postgres;

--
-- Name: poi_id_seq; Type: SEQUENCE; Schema: semantic; Owner: postgres
--

CREATE SEQUENCE semantic.poi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE semantic.poi_id_seq OWNER TO postgres;

--
-- Name: poi_id_seq; Type: SEQUENCE OWNED BY; Schema: semantic; Owner: postgres
--

ALTER SEQUENCE semantic.poi_id_seq OWNED BY semantic.poi.id;


--
-- Name: poi id; Type: DEFAULT; Schema: semantic; Owner: postgres
--

ALTER TABLE ONLY semantic.poi ALTER COLUMN id SET DEFAULT nextval('semantic.poi_id_seq'::regclass);


--
-- Name: oa oa_pkey; Type: CONSTRAINT; Schema: semantic; Owner: postgres
--

ALTER TABLE ONLY semantic.oa
    ADD CONSTRAINT oa_pkey PRIMARY KEY (oa11);


--
-- Name: pcd pcd_pkey; Type: CONSTRAINT; Schema: semantic; Owner: postgres
--

ALTER TABLE ONLY semantic.pcd
    ADD CONSTRAINT pcd_pkey PRIMARY KEY (pcd);


--
-- Name: poi poi_pkey; Type: CONSTRAINT; Schema: semantic; Owner: postgres
--

ALTER TABLE ONLY semantic.poi
    ADD CONSTRAINT poi_pkey PRIMARY KEY (id);


--
-- Name: pcd pcd_oa11_fkey; Type: FK CONSTRAINT; Schema: semantic; Owner: postgres
--

ALTER TABLE ONLY semantic.pcd
    ADD CONSTRAINT pcd_oa11_fkey FOREIGN KEY (oa11) REFERENCES semantic.oa(oa11);


--
-- PostgreSQL database dump complete
--

