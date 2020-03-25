from dotenv import load_dotenv, find_dotenv
import os

def load():
    load_dotenv(find_dotenv())

def get_mariadb():
    MARIADB_HOST = os.environ['MARIADB_HOST']
    MARIADB_DB = os.environ['MARIADB_DB']
    MARIADB_USER = os.environ['MARIADB_USER']
    MARIADB_PASSWORD = os.environ['MARIADB_PASSWORD']
    MARIADB_PORT = os.environ['MARIADB_PORT']
    
    mariadb_credentials = {'host': MARIADB_HOST,
                        'dbname': MARIADB_DB,
                        'user': MARIADB_USER,
                        'password': MARIADB_PASSWORD,
                        'port': MARIADB_PORT}
    
    return mariadb_credentials

def get_root_dir():
    ROOT_FOLDER = os.environ['ROOT_FOLDER']
    return ROOT_FOLDER

def get_otp_settings():
    LOAD_BALANCER_HOST = os.environ['LOAD_BALANCER_HOST']
    LOAD_BALANCER_PORT = os.environ['LOAD_BALANCER_PORT']
    NUM_THREADS = os.environ['NUM_THREADS']
    return LOAD_BALANCER_HOST, LOAD_BALANCER_PORT, NUM_THREADS

