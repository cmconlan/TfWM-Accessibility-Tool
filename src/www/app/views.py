from app import app, db
from flask import jsonify
from sqlalchemy import text
import os
import json
import re


def execute_query(sql_string):
    query = text(sql_string)
    return db.engine.execute(query)


def get_key_value_pairs(db_results):
    pairs = []
    for (value,) in db_results:
        if not title_case(value):
            pairs.append(key_value_pair(value, humanise(value)))
        else:
            pairs.append(key_value_pair(value, value))
    return pairs


def key_value_pair(key, value):
    return { 'key': key, 'value': value } 


def title_case(string):
    first_char = string[0]
    return '_' not in string and first_char == first_char.upper()


def find_prefix(strs):
    longest_pre = ""
    if not strs:
        return longest_pre
    shortest_str = min(strs, key=len)
    for i in range(len(shortest_str)):
        if all([x.startswith(shortest_str[:i+1]) for x in strs]):
            longest_pre = shortest_str[:i+1]
        else:
            break
    return longest_pre


def remove_common_prefix(strings):
    prefix = find_prefix(strings)
    return [string.replace(prefix, '') for string in strings]
        


def humanise(string):
    string_list = string.split('_')
    return_string = ''
    for substring in string_list:
        if len(substring) > 1:
            return_string += substring[0].upper() + substring[1:]
        else:
            return_string += substring.upper()
        return_string += ' '
    return return_string.strip()


    


def get_json(db_results):
    key_value_pairs = get_key_value_pairs(db_results)
    return jsonify(key_value_pairs)


@app.route("/meta/accessibility-metric")
def get_accessibility_metric():
    results = execute_query("SELECT sql FROM sqlite_master WHERE tbl_name = 'otp_results_summary' AND type = 'table'")
    result = str(results.fetchall())
    # Match strings of the form sum_x_y
    metrics = remove_common_prefix(re.findall('sum_[a-z_]*', result))
    if metrics:
        pairs = [key_value_pair(metric, humanise(metric)) for metric in metrics]
        return jsonify(pairs)
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/meta/time-strata")
def get_time_strata():
    results = execute_query("SELECT DISTINCT stratum FROM otp_results_summary")
    return get_json(results)


@app.route("/meta/point-of-interest-type")
def get_poi_type():
    results = execute_query("SELECT DISTINCT type FROM poi")
    return get_json(results)


@app.route("/meta/population-metric")
def get_population_metric():
    metrics = json.loads(app.config['POPULATION_METRICS'])
    pairs = [key_value_pair(metric, humanise(metric)) for metric in metrics]
    return jsonify(pairs)


@app.route("/meta/demographic")
def get_meta_demographic():
    results = execute_query("SELECT DISTINCT population FROM populations")
    return get_json(results)


@app.route("/output-areas")
def get_output_areas():
    # Using a relative path e.g ./geo_simp.json results in an empty file
    file_dir = os.path.dirname(__file__)
    with open(os.path.join(file_dir, 'geo_simp.json'), 'r') as json_file:
        return json_file.read()


@app.route("/population-metrics")
def get_population_metrics():
    return "[]"


@app.route("/accessibility-metrics")
def get_metrics():
    return "[]"
