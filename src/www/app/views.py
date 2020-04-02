import os
import json
import re
from app import app
from flask import jsonify, request, make_response
from app.utils import execute_query, get_key_value_pairs, remove_common_prefix, calculate_access_metric
from app.utils import  population_density, at_risk_scores, get_json, add_rank

@app.route("/meta/accessibility-metric")
def get_accessibility_metric():
    results = execute_query("SELECT sql FROM sqlite_master WHERE tbl_name = 'otp_results_summary' AND type = 'table'")
    result = str(results.fetchall())
    # Match strings of the form sum_x_y
    metrics = remove_common_prefix(re.findall('sum_[a-z_]*', result))
    if metrics:
        return jsonify(get_key_value_pairs(metrics))
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
    return jsonify(get_key_value_pairs(metrics))


@app.route("/meta/demographic")
def get_meta_demographic():
    results = execute_query("SELECT DISTINCT population FROM populations")
    return get_json(results)


@app.route("/output-areas")
def get_output_areas():
    # Using a relative path e.g ./geo_simp.json results in an empty file
    file_dir = os.path.dirname(__file__)
    with open(os.path.join(file_dir, 'geo_simp.json'), 'r') as json_file:
        return jsonify(json.load(json_file))


@app.route("/population-metrics", methods=['GET'])
def population_metrics():
    metric = request.args.get('population-metric', 'population_density')
    demographic_groups = request.args.getlist('demographic-group')
    if metric == 'population_density':
        density = population_density(demographic_groups)
        return jsonify(add_rank(density))
    elif metric == 'at-risk_score':
        poi_types = request.args.getlist('point-of-interest-types')
        time_strata = request.args.getlist('time-strata')
        at_risk_score = at_risk_scores(demographic_groups, poi_types, time_strata)
        return jsonify(add_rank(at_risk_score))
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/accessibility-metrics", methods=['GET'])
def accessibility_metrics():
    access_metric = request.args.get('accessibility-metric', 'gen_cost')
    poi_types = request.args.getlist('point-of-interest-types')
    time_strata = request.args.getlist('time-strata')
    access_metrics = calculate_access_metric(access_metric, poi_types, time_strata)
    if 'error' in access_metrics:
        return make_response(access_metrics, 404)
    else:
        return jsonify(add_rank(access_metrics))
