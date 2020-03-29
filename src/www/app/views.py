from app import app
from app import engine
from sqlalchemy import text


@app.route("/metrics")
def get_metrics():
    return "/metrics"


@app.route("/meta/ethnicity")
def get_meta_ethnicity(): 
    query = text(
        """SELECT column_name FROM information_schema.columns 
        WHERE column_name LIKE 'eth%'"""
    )
    with engine.connect() as connection:
        ethnicities = connection.execute(query)
    
    return "[]"


@app.route("/meta/employment-status")
def get_meta_employment_status():
    return "[]"


@app.route("/meta/disability-status")
def get_meta_disability_status():
    return "[]"


@app.route("/meta/accessibility-metric")
def get_accessibility_metric():
    return "[]"


@app.route("/meta/geographic-area")
def get_geographic_area():
    return "[]"


@app.route("/meta/time-strata")
def get_time_strata():
    return "[]"


@app.route("/meta/point-of-interest-type")
def get_poi_type():
    return "[]"
