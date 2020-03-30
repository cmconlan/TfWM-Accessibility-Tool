from app import app
from sqlalchemy import text


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
    ## SELECT oa_id from oa;
    return "[]"


@app.route("/population-metrics")
def get_population_metrics():
    return "[]"
