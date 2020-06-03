
import os
path = '/home/chris/Documents/TfWM-Accessibility-Tool/src/'
os.chdir(path)
import settings
from modeling import model_functions
from etl.load_raw import load_data_dict, load_text, load_gis, load_osm
from utils import *

suffix=''
mode='replace'
settings.load()
ROOT_FOLDER = settings.get_root_dir()
SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')
RESULTS_FOLDER = os.path.join(ROOT_FOLDER, 'results/')
psql_credentials = settings.get_psql()

# Create SQLAlchemy engine from database credentials
engine = create_connection_from_dict(psql_credentials, 'postgresql')
print('Database connected')

#%% Finish ETL Processing

print("Transfer OSM data to raw")
execute_sql(os.path.join(SQL_FOLDER,'update_osm_tables.sql'), engine, read_file=True)

## ---- CLEAN DATA TO CLEANED SCHEMA ----
print("Cleaning data")
execute_sql(os.path.join(SQL_FOLDER, 'clean_data.sql'), engine, read_file=True)

## ---- ENTITIZE DATA TO SEMANTIC SCHEMA ----
print("Entitizing data")
execute_sql(os.path.join(SQL_FOLDER, 'create_semantic.sql'), engine, read_file=True)

#%%

# Load model configuration
model_config = os.path.join(ROOT_FOLDER, 'config/base/model_config.yaml')
print('Configure models')
params = load_yaml(model_config)
population_dict = params.get('populations')
poi_dict = params.get('points_of_interest')
time_defs = params.get('time_defs')
time_strata = params.get('time_strata')
hyper_params = params.get('hyper_params')
metrics = params.get('metrics')
print('Model parameters loaded')


# Sample timestamps and write to MODEL.timestamps
model_functions.create_timestamps(time_defs, time_strata, n_timepoints=hyper_params.get('n_timepoint'), engine=engine, suffix=suffix)

# Generate MODEL.k_poi (K-nearest POIs)
model_functions.create_k_poi(SQL_FOLDER, k_poi=hyper_params.get('k_POI'), poi_dict=poi_dict, suffix=suffix, engine=engine)

# Configure OTP query parameters and save to MODEL.trips
model_functions.create_trips(SQL_FOLDER, suffix=suffix, engine=engine, mode=mode)

# Generate RESULTS.populations
model_functions.compute_populations(SQL_FOLDER, population_dict, engine)

#create otp trips

execute_sql(os.path.join(SQL_FOLDER,'create_model_otp_trips.sql'), engine, read_file=True)