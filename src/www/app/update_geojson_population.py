import sys
import os
import json
 # Add the www directory to the python path so the db from the app module is available
sys.path.append('/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/src/www')
from app import db

results = db.engine.execute(
    "SELECT oa_id, count FROM populations WHERE population = 'total'"
).fetchall()

populations = { oa_id: population for oa_id, population in results }

file_dir = os.path.dirname(__file__)
with open(os.path.join(file_dir, 'geo_simp.json'), 'r') as json_file:
    geo_json = json.load(json_file)

for feature in geo_json['features']:
    feature['properties']['population'] = populations[feature['id']]

with open(os.path.join(file_dir, 'geo_simp.json'), 'w') as json_file:
    json_file.write(json.dumps(geo_json))
