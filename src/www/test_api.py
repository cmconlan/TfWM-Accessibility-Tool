import pytest
import mysql.connector as mariadb
import json
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def execute_query(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


def humanise(string, prefix):
    string = string.replace(prefix, '')
    string_list = string.split('_')
    return_string = ''
    for substring in string_list:
        return_string += substring[0].upper() + substring[1:] + ' '
    return return_string.strip()


def get_key_value_pair(key, prefix):
    return { 'key': key, 'value': humanise(key, prefix) }


def find_prefix(strs):
    longest_pre = ""
    if not strs:
        return longest_pre
    strs = [string for (string,) in strs]
    shortest_str = min(strs, key=len)
    for i in range(len(shortest_str)):
        if all([x.startswith(shortest_str[:i+1]) for x in strs]):
            longest_pre = shortest_str[:i+1]
        else:
            break
    return longest_pre


def get_key_value_pair_list(query_response):
    prefix = find_prefix(query_response)
    expected = []
    for row in query_response:
        expected.append(get_key_value_pair(row[0], prefix))
    return expected


def test_humanise():
    assert humanise('eth_all', 'eth_') == 'All'
    assert humanise('eth_white', 'eth_') == 'White'
    assert humanise('eth_gypsy', 'eth_') == 'Gypsy'
    assert humanise('eth_mixed', 'eth_') == 'Mixed'
    assert humanise('eth_asian_indian', 'eth_') == 'Asian Indian'
    assert humanise('PerfectlyNormal', '') == "PerfectlyNormal"


def test_doc_root(client):
    response = client.get('/')
    assert b'Hello world' in response.data


def test_meta_ethnicity(client):
    ethnicities = execute_query(
        """SELECT column_name FROM information_schema.columns 
        WHERE column_name LIKE 'eth%'"""
    )
    expected = get_key_value_pair_list(ethnicities)
    response = client.get("/meta/ethnicity")
    response_list = json.loads(response.data)
    assert response_list == expected


def test_meta_employment_status(client):
    statuses = execute_query(
        """SELECT column_name FROM information_schema.columns 
        WHERE column_name LIKE 'emp_%' AND column_name<>'EMPTY_QUERIES'"""
    )
    expected = get_key_value_pair_list(statuses)
    response = client.get("/meta/employment-status")
    response_list = json.loads(response.data)
    assert response_list == expected


def test_meta_disability_status(client):
    statuses = execute_query(
        """SELECT column_name FROM information_schema.columns WHERE column_name like 'disability%'"""
    )
    expected = get_key_value_pair_list(statuses)
    response = client.get("/meta/disability-status")
    response_list = json.loads(response.data)
    assert response_list == expected


def test_accessibility_metric(client):
    response = client.get("/meta/accessibility-metric")


def test_geographic_area(client):
    output_areas = execute_query(
        """SELECT oa_id from oa"""
    )
    expected = []
    for (output_area,) in output_areas:
        expected.append({
            'key': output_area,
            'value': output_area
        })

    response = client.get("/meta/geographic-area")
    response_list = json.loads(response.data)
    assert response_list == expected


def test_time_strata(client):
    strata = execute_query(
        """SELECT * FROM stratum_types"""
    )
    expected = []
    for (stratum,) in strata:
        expected.append({
            'key': stratum,
            'value': stratum
        })
    response = client.get("/meta/time-strata")
    response_list = json.loads(response.data)
    assert response_list == expected


def test_poi_type(client):
    poi_types = execute_query(
        """SELECT DISTINCT type FROM poi"""
    )
    expected = []
    for (poi_type,) in poi_types:
        expected.append({
            'key': poi_type,
            'value': poi_type
        })

    response = client.get("/meta/point-of-interest-type")
    response_list = json.loads(response.data)
    assert response_list == expected
