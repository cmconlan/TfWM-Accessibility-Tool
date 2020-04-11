import json
import os
from functools import reduce
import pytest
from app import app, db
import app.utils as utils
from config import basedir

@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_meta_accessibility_metrics(client):
    [create_statement] = fetch_expected("""SELECT sql FROM sqlite_master 
        WHERE tbl_name = 'otp_results_summary' AND type = 'table'""")
 
    response = client.get("/meta/accessibility-metric")
    response_list = json.loads(response.data)
    assert response_has_expected_keys(get_response_keys(response_list), create_statement)


def test_meta_time_strata(client):
    query = "SELECT DISTINCT stratum FROM trip_strata"
    response = client.get("/meta/time-strata")
    verify_response_against_query(response, query)


def test_meta_demographic(client):
    query = "SELECT DISTINCT population FROM populations WHERE population <> 'total'"
    response = client.get("/meta/demographic")
    verify_response_against_query(response, query)


def test_meta_poi_type(client):
    query = "SELECT DISTINCT type FROM poi"
    response = client.get("/meta/point-of-interest-type")
    verify_response_against_query(response, query)


def test_meta_population_metrics(client):
    response = client.get('/meta/population-metric')
    metrics = json.loads(app.config['POPULATION_METRICS'])
    response_list = json.loads(response.data)
    response_keys = get_response_keys(response_list)

    assert expected_number_of_results(metrics, response_list)
    assert no_duplicates(response_keys)
    assert response_has_expected_keys(response_keys, metrics)


def test_population_density(client):
    demographics = fetch_expected("SELECT DISTINCT population FROM populations")
    demographic_subsets = get_subsequences(demographics)
    oa_ids = get_oa_ids()
    base_url = '/population-metrics?population-metric=population_density'
    for subset in demographic_subsets:
        query_url = construct_query_params(base_url,'demographic-group', subset)
        density = utils.population_density(subset)
        response = json.loads(client.get(query_url).data)
        assert contains_all_output_areas(oa_ids, response)
        if not metrics_match_expected(response, density):
            print(query_url)
            pytest.fail()


def test_accessibility_metrics(client):
    access_metrics = ['journey_time', 'walking_distance', 'fare', 'generalised_cost']
    time_strata_seq = get_subsequences(fetch_expected("SELECT DISTINCT stratum FROM otp_results_summary"))
    poi_types_seq = get_subsequences(fetch_expected("SELECT DISTINCT type FROM poi"))
    oa_ids = get_oa_ids()
    for metric in access_metrics:
        base_url = '/accessibility-metrics?' + 'accessibility-metric=' + metric
        for poi_types in poi_types_seq:
            for strata in time_strata_seq:
                query_url = construct_query_params(base_url, 'point-of-interest-types', poi_types)
                query_url = construct_query_params(query_url, 'time-strata', strata)
                print(query_url)
                metrics = utils.calculate_access_metric(metric, poi_types, strata)
                response = json.loads(client.get(query_url).data)
                assert contains_all_output_areas(oa_ids, response)
                if not metrics_match_expected(response, metrics):
                    print(query_url)
                    pytest.fail()


def verify_response_against_query(response, sql_query):
    query_results = fetch_expected(sql_query)

    response_list = json.loads(response.data)
    response_keys = get_response_keys(json.loads(response.data))

    assert expected_number_of_results(query_results, response_list)
    assert no_duplicates(response_keys)
    assert response_has_expected_keys(response_keys, query_results)


def fetch_expected(sql_query):
    results = db.engine.execute(sql_query)
    return [result for (result,) in results]


def get_response_keys(response):
    return [kv['key'] for kv in response]


def expected_number_of_results(expected, results):
    return len(expected) == len(results)


def no_duplicates(results):
    return len(results) == len(set(results))


def response_has_expected_keys(results, expected):
    for key in results:
        if key not in expected:
            return False
    return True


def get_subsequences(input_list):
    lists = []
    for i in range(len(input_list)+1):
        lists.append(input_list[0:i])
    return lists


# Use this to test all possible subsets of inputs
# Takes a very long time however
def get_subsets(input_list):
    if not input_list:
        return [[]]
    else:
        head, *tail = input_list
        prev_combinations = get_subsets(tail)
        for combination in prev_combinations:
            if head not in combination:
                new = combination + [head]
                prev_combinations.append(new)
        return prev_combinations


def construct_query_params(base_url, name, parameters):
    for parameter in parameters:
        base_url += f'&{name}={parameter}'
    return base_url


def get_oa_ids():
    with open(os.path.join(basedir, 'app/geo_simp.json'), 'r') as json_file:
        geo_json = json.load(json_file)
        oa_ids = [feature['id'] for feature in geo_json['features']]
    return oa_ids


def contains_all_output_areas(output_areas, metrics):
    for oa_id in metrics:
        if oa_id not in output_areas:
            return False
    return True
    

def metrics_match_expected(results, expected):
    for oa_id in expected:
        if results[oa_id]['metric'] != expected[oa_id]:
            print(results[oa_id]['metric'], expected[oa_id])
            print(oa_id, results[oa_id], expected[oa_id])
            return False
    return True
