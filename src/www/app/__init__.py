import sys
sys.path.append('/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/src')
from flask import Flask
from utils import create_connection_from_dict
import settings


settings.load()
credentials = settings.get_mariadb()
engine = create_connection_from_dict(credentials, 'mysql+mysqldb')
db = engine.connect()

app = Flask(__name__)
from app import views

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db.close()
