
import os
import logging
import settings
import progressbar as pb
from modeling import model_functions
from utils.utils import load_yaml, load_data_dict
from utils.database import Database

STEPS = 13
steps_iter = iter(range(1, STEPS+1))
logger = settings.configure_logger()
ROOT_FOLDER = settings.get_root_dir()
DATA_FOLDER = os.path.join(ROOT_FOLDER, 'data/')
SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')
RESULTS_FOLDER = os.path.join(ROOT_FOLDER, 'results/')
data_config = os.path.join(ROOT_FOLDER, 'config/base/data_files.yaml')


database = Database.get_instance()

with pb.ProgressBar(max_value=13) as bar:
    logger.info("Creating schemas")
    database.execute_sql(
        os.path.join(SQL_FOLDER,'create_schemas.sql'),
        read_file=True
    )
    bar.update(next(steps_iter))

    logger.info("Creating tables")
    database.execute_sql(
        os.path.join(SQL_FOLDER, 'create_tables.sql'),
        read_file=True
    )
    bar.update(next(steps_iter))

    text_dict, gis_dict, osm_file = load_data_dict(data_config)
    bar.update(next(steps_iter))

    logger.info("Loading text files to RAW")
    database.load_text(DATA_FOLDER, text_dict)
    bar.update(next(steps_iter))

    logger.info("Loading shapefiles to GIS")
    database.load_gis(DATA_FOLDER, gis_dict)
    bar.update(next(steps_iter))

    logger.info("Loading OSM data to RAW")
    database.load_osm_to_db(
        DATA_FOLDER, 
        osm_file, 
        os.path.join(SQL_FOLDER, 'update_osm_tables.sql'), 
    )
    bar.update(next(steps_iter))

    logger.info("Cleaning data")
    database.execute_sql(
        os.path.join(SQL_FOLDER, 'clean_data.sql'), 
        read_file=True
    )
    bar.update(next(steps_iter))

    logger.info("Entitizing data")
    database.execute_sql(
        os.path.join(SQL_FOLDER, 'create_semantic.sql'),
        read_file=True
    )
    bar.update(next(steps_iter))

    model_config = os.path.join(ROOT_FOLDER, 'config/base/model_config.yaml')
    params = load_yaml(model_config)
    hyper_params = params['hyper_params']
    logger.info('Model parameters loaded')
    bar.update(next(steps_iter))

    logger.info('Creating timestamps')
    model_functions.create_timestamps(
        params['time_defs'], 
        params['time_strata'], 
        n_timepoints=hyper_params['n_timepoint'],
    )
    bar.update(next(steps_iter))

    logger.info('Selecting K nearest Points of Interest for each OA')
    model_functions.create_k_poi(
        SQL_FOLDER, 
        k_poi=hyper_params['k_POI'],
        poi_dict=params['points_of_interest'],
    )
    bar.update(next(steps_iter))

    logger.info('Creating possible combinations of trips for OTP input')
    model_functions.create_trips(SQL_FOLDER)
    database.execute_sql(
        os.path.join(SQL_FOLDER, 'create_model_otp_trips.sql'), 
        read_file=True
    )
    bar.update(next(steps_iter))

    file_name = 'otp_trips'
    logger.info(f'Storing model.{file_name} to {file_name}.csv')
    database.copy_table_to_csv(
        f'model.{file_name}',
        os.path.join(RESULTS_FOLDER, f'{file_name}.csv'),
    )
