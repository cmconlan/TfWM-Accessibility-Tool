
import os
import logging
import settings
from etl.load_raw import load_data_dict, load_text, load_gis, load_osm
from modeling import model_functions
from utils import *
import progressbar as pb


logger = settings.configure_logger()
#%%
mode='replace'
settings.load()
ROOT_FOLDER = settings.get_root_dir()
DATA_FOLDER = os.path.join(ROOT_FOLDER, 'data/')
SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')
RESULTS_FOLDER = os.path.join(ROOT_FOLDER, 'results/')
data_config = os.path.join(ROOT_FOLDER, 'config/base/data_files.yaml')

#%%
psql_credentials = settings.get_psql()

engine = create_connection_from_dict(psql_credentials, 'postgresql')

#%%

logger.info("Creating schemas")
execute_sql(
    os.path.join(SQL_FOLDER,'create_schemas.sql'),
    engine,
    read_file=True
)

#%%

logger.info("Creating tables")
execute_sql(
    os.path.join(SQL_FOLDER, 'create_tables.sql'),
    engine,
    read_file=True
)

#%%

text_dict, gis_dict, osm_file = load_data_dict(data_config)

#%%

logger.info("Loading text files to RAW")
load_text(DATA_FOLDER, text_dict, engine)

#%%

logger.info("Loading shapefiles to GIS")
load_gis(DATA_FOLDER, gis_dict, psql_credentials)

logger.info("Loading OSM data to RAW")
load_osm(
    DATA_FOLDER, 
    osm_file, 
    psql_credentials, 
    os.path.join(SQL_FOLDER, 'update_osm_tables.sql'), 
    engine
)

logger.info("Cleaning data")
execute_sql(
    os.path.join(SQL_FOLDER, 
    'clean_data.sql'), 
    engine, 
    read_file=True
)

logger.info("Entitizing data")
execute_sql(
    os.path.join(SQL_FOLDER, 'create_semantic.sql'),
    engine, 
    read_file=True
)
#%%

model_config = os.path.join(ROOT_FOLDER, 'config/base/model_config.yaml')
params = load_yaml(model_config)
population_dict = params.get('populations')
poi_dict = params.get('points_of_interest')
time_defs = params.get('time_defs')
time_strata = params.get('time_strata')
hyper_params = params.get('hyper_params')
metrics = params.get('metrics')
logger.info('Model parameters loaded')

logger.info('Creating timestamps')
model_functions.create_timestamps(
    time_defs, 
    time_strata, 
    n_timepoints=hyper_params.get('n_timepoint'),
    engine=engine
)

logger.info('Selecting K nearest Points of Interest for each OA')
model_functions.create_k_poi(
    SQL_FOLDER, 
    k_poi=hyper_params.get('k_POI'),
    poi_dict=poi_dict,
    engine=engine
)

logger.info('Creating possible combinations of trips for OTP input')
model_functions.create_trips(
    SQL_FOLDER, 
    engine=engine,
    mode=mode
)

model_functions.compute_populations(
    SQL_FOLDER, population_dict, engine)

execute_sql(
    os.path.join(SQL_FOLDER, 'create_model_otp_trips.sql'), 
    engine, 
    read_file=True
)

file_name = 'otp_trips'
logger.info(f'Storing model.{file_name} to {file_name}.csv')
copy_table_to_csv(
    f'model.{file_name}',
    os.path.join(RESULTS_FOLDER, f'{file_name}.csv'),
    engine
)
