from app import app


@app.route("/")
def index():
    return "Hello world!"


@app.route("/metrics")
def get_metrics():
    return "/metrics"


@app.route("/meta/ethnicity")
def get_meta_ethnicity():
    return "/meta/ethnicity"


@app.route("/meta/employment-status")
def get_meta_employment_status():
    return "/meta/employment-status"


@app.route("/meta/disability-status")
def get_meta_disability_status():
    return "/meta/disability-status"


@app.route("/meta/accessibility-metric")
def get_accessibility_metric():
    return "/meta/accessibility-metric"


@app.route("/meta/geographic-area")
def get_geographic_area():
    return "/meta/geographic-area"


@app.route("/meta/time-strata")
def get_time_strata():
    return "/meta/time-strata"


@app.route("/meta/point-of-interest-type")
def get_poi_type():
    return "/meta/point-of-interest-type"
