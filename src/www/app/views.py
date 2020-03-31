from app import app, db
from flask import jsonify, request, make_response
from sqlalchemy import text
import os
import json
import re


def execute_query(sql_string, args=None):
    if args:
        return db.engine.execute(sql_string, *args)
    else:
        return db.engine.execute(sql_string)


def get_key_value_pairs(db_results):
    
    def title_case(string):
        first_char = string[0]
        return '_' not in string and first_char == first_char.upper()
    
    pairs = []
    for (value,) in db_results:
        if not title_case(value):
            pairs.append(key_value_pair(value, humanise(value)))
        else:
            pairs.append(key_value_pair(value, value))
    return pairs


def key_value_pair(key, value):
    return { 'key': key, 'value': value } 


# Shamelessly stolen from
# https://medium.com/@d_dchris/10-methods-to-solve-the-longest-common-prefix-problem-using-python-leetcode-14-a87bb3eb0f3a
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


def get_population_density(demographic_groups):
    if not demographic_groups:
        where_clause = ''
    else:
        where_clause = f'WHERE population IN {construct_where_clause_args(len(demographic_groups))}'
    query = (f"SELECT oa_id, sum(count) AS pop_count "
            f"FROM populations {where_clause} "
            f"GROUP BY oa_id "
            f"ORDER BY pop_count DESC")
    pairs = []
    args = [(index+1, value) for index, value in enumerate(demographic_groups)]
    for (oa_id, pop_count) in execute_query(query, demographic_groups):
        pairs.append(get_metric(oa_id, pop_count))
    return jsonify(pairs)


def construct_where_clause_args(num_args):
    if num_args == 0:
        return ''
    elif num_args == 1:
        return '(?)'
    else:
        return str(tuple('?' for i in range(num_args))).replace("'", "")


def get_metric(oa_id, metric_value):
    return {'output_area_id': oa_id, 'metric': metric_value}


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


@app.route("/population-metrics", methods=['GET'])
def get_population_metrics():
    metric = request.args.get('population-metric', 'population_density')
    demographic_groups = request.args.getlist('demographic-group')
    if metric == 'population_density':
        return get_population_density(demographic_groups)
    elif metric == 'at-risk_score':
        pass #TODO return at-risk score
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/accessibility-metrics", methods=['GET'])
def get_metrics():
    access_metric = request.args.get('accessibiltiy-metric', 'sum_gen_cost')
    poi_types = request.args.get('point-of-interest-types')
    time_strata = request.args.get('time-strata')
    where_clause = ''
    if poi_types or time_strata:
        where_clause = 'WHERE '
        poi_str = ''
        strata_str = ''
        if poi_types:
            poi_str = 'poi_type IN ' + construct_where_clause_args(poi_types)
        if time_strata:
            strata_str = 'stratum IN ' + construct_where_clause_args(time_strata)

        if poi_str and strata_str:
            where_clause += f'{poi_str} AND {strata_str}'
        else:
            where_clause += poi_str + strata_str
    
    query = (f"SELECT oa_id, sum(:metric) / sum(num_trips) "
            f"FROM otp_results_summary {where_clause} GROUP BY oa_id")
    execute_query(query, metric=access_metric)
    # TODO finish
    return "[]"
