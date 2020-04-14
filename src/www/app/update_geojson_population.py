import sys
import os
import json
 # Add the www directory to the python path so the db from the app module is available
sys.path.append('/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/src/www')
from app import db

# Get the population for each OA from the database, and construct a dict
# indexed by OA ID.
results = db.engine.execute(
    "SELECT oa_id, count FROM populations WHERE population = 'total'"
).fetchall()
populations = { oa_id: population for oa_id, population in results }

# Open the GeoJSON file and parse the contents to a dict.
file_dir = os.path.dirname(__file__)
with open(os.path.join(file_dir, 'geo_simp.json'), 'r') as json_file:
    geo_json = json.load(json_file)

# Set the population field for each OA to be the population we got from the database
for feature in geo_json['features']:
    feature['properties']['population'] = populations[feature['id']]

# Open the file and overwrite the contents with the updated json.
# The output is not formatted so the whole json just resides on one line.
# Can be formatted with VSCode.
with open(os.path.join(file_dir, 'geo_simp.json'), 'w') as json_file:
    json_file.write(json.dumps(geo_json))
