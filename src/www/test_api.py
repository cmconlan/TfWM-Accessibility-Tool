import json
from functools import reduce
import pytest
import mysql.connector as mariadb
from app import app, db


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
    query = "SELECT DISTINCT population FROM populations"
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
    keys_in_expected = map(lambda key: key in expected, results)
    all_keys_in_expected = reduce(lambda x, y: x and y, keys_in_expected)
    return all_keys_in_expected
