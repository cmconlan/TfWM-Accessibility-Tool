from app import app

@app.route("/")
def index():
    return "Hello world!"

@app.route("/metrics")
def api_return_metrics():
    return "/metrics"