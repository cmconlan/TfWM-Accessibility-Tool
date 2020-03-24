import os
import settings
from modeling import model_functions
from utils import load_yaml, create_connection_from_dict

chunksize = 10000
suffix = ''

if __name__ == '__main__':

    settings.load()

    ROOT_FOLDER = settings.get_root_dir()
    SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')
    RESULTS_FOLDER = os.path.join(ROOT_FOLDER, 'results/')

    mariadb_credentials = settings.get_mariadb()

    host, port, num_splits = settings.get_otp_settings()

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

    # Create SQLAlchemy engine from database credentials
    engine = create_connection_from_dict(mariadb_credentials, 'mysql+mysqldb')
    print('Database connected')

    model_functions.split_trips(host, port, num_splits, SQL_FOLDER, RESULTS_FOLDER,
                            engine, mariadb_credentials, suffix=suffix, chunksize=chunksize)
