from dotenv import load_dotenv, find_dotenv
import os

def load():
    # DotEnv starts searching at / for some reason, therefore need to keep 
    # .env relative to settings.py
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def get_mariadb():
    MARIADB_HOST = os.environ['MARIADB_HOST']
    MARIADB_DB = os.environ['MARIADB_DB']
    MARIADB_USER = os.environ['MARIADB_USER']
    MARIADB_PASSWORD = os.environ['MARIADB_PASSWORD']
    MARIADB_PORT = os.environ['MARIADB_PORT']
    
    mariadb_credentials = {
        'host': MARIADB_HOST,
        'dbname': MARIADB_DB,
        'user': MARIADB_USER,
        'password': MARIADB_PASSWORD,
        'port': MARIADB_PORT
    }
    
    return mariadb_credentials

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
    LOAD_BALANCER_HOST = os.environ['LOAD_BALANCER_HOST']
    LOAD_BALANCER_PORT = os.environ['LOAD_BALANCER_PORT']
    NUM_PROCESSES = os.environ['NUM_PROCESSES']
    NUM_OTPS = os.environ['NUM_OTPS']
    return LOAD_BALANCER_HOST, LOAD_BALANCER_PORT, NUM_PROCESSES, NUM_OTPS

