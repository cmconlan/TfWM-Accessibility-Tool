from app import app
from flask import jsonify
import os

@app.route("/accessibility-metrics")
def get_metrics():
    return "[]"


@app.route("/meta/accessibility-metric")
def get_accessibility_metric():
    return "[]"


@app.route("/meta/time-strata")
def get_time_strata():
    return "[]"


@app.route("/meta/point-of-interest-type")
def get_poi_type():
    return "[]"


@app.route("/meta/population-metric")
def get_population_metric():
    return "[]"


@app.route("/meta/demographic")
def get_meta_demographic(): 
    return "[]"


@app.route("/output-areas")
def get_output_areas():
    file_dir = os.path.dirname(__file__)
    with open(os.path.join(file_dir, 'geo_simp.json'), 'r') as json_file:
        return json_file.read()


@app.route("/population-metrics")
def get_population_metrics():
    return "[]"
