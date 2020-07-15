from dotenv import load_dotenv, find_dotenv
import os
import logging
import progressbar

# DotEnv starts searching at / for some reason, therefore need to keep 
# .env relative to settings.py
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def get_psql():
    PSQL_HOST = os.environ['PSQL_HOST']
    PSQL_DB = os.environ['PSQL_DB']
    PSQL_USER = os.environ['PSQL_USER']
    PSQL_PASSWORD = os.environ['PSQL_PASSWORD']
    PSQL_PORT = os.environ['PSQL_PORT']
    psql_credentials = {
        'host': PSQL_HOST,
        'dbname': PSQL_DB,
        'user': PSQL_USER,
        'password': PSQL_PASSWORD,
        'port': PSQL_PORT
    }
    return psql_credentials


def get_root_dir():
    ROOT_FOLDER = os.environ['ROOT_FOLDER']
    return ROOT_FOLDER


def get_otp_settings():
    OTP_HOST = os.environ['OTP_HOST']
    OTP_PORT = int(os.environ['OTP_PORT'])
    NUM_PROCESSES = int(os.environ['NUM_PROCESSES'])
    NUM_OTPS = int(os.environ['NUM_OTPS'])
    return OTP_HOST, OTP_PORT, NUM_PROCESSES, NUM_OTPS


def get_sqlite_settings():
    PATH = os.environ['SQLITE_PATH']
    return PATH


def get_environment_variable(var: str) -> str:
    return os.environ[var]


def configure_logger():
    # Make sure to redirect stderr for the progress bar
    # before instantiating the logger.
    progressbar.streams.wrap_stderr()

    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('./etl_and_model.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S:'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    # Don't necessarily have to return the logger
    # as its available globally from the logging module,
    # but this saves having to write logging.getLogger()
    return logger
