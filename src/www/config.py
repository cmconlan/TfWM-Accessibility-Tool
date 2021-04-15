import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    PORT = os.environ.get('PORT') or 7161
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'tfwm.db')
    POPULATION_METRICS = os.environ.get('POPULATION_METRICS')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
