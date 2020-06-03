
import os
path = '/home/chris/Documents/TfWM-Accessibility-Tool/src/'
os.chdir(path)
import settings
from etl.load_raw import load_data_dict, load_text, load_gis, load_osm
from utils import *

#%%

settings.load()
# Get environment folders
ROOT_FOLDER = settings.get_root_dir()
DATA_FOLDER = os.path.join(ROOT_FOLDER, 'data/')
SQL_FOLDER = os.path.join(ROOT_FOLDER, 'sql/')

# Data files to be loaded
data_config = os.path.join(ROOT_FOLDER, 'config/base/data_files.yaml')

#%%
# Get PostgreSQL database credentials 
psql_credentials = settings.get_psql()

# Create SQLAlchemy engine from database credentials
engine = create_connection_from_dict(psql_credentials, 'postgresql')

#%%

print("Creating schemas")
execute_sql(os.path.join(SQL_FOLDER,'create_schemas.sql'), engine, read_file=True)

#%%

## ---- CREATE TABLES WITHIN RAW SCHEMA ----
print("Creating tables")
execute_sql(os.path.join(SQL_FOLDER, 'create_tables.sql'), engine, read_file=True)

#%%

## ---- LOAD RAW DATA TO DATABASE ----
text_dict, gis_dict, osm_file = load_data_dict(data_config)

#%%

# Load CSV file to RAW schema
print("Loading text files to RAW")
load_text(DATA_FOLDER, text_dict, engine)

#%%

# Load GIS data to GIS schema
print("Loading shapefiles to GIS")
load_gis(DATA_FOLDER, gis_dict, psql_credentials)

#%%

# Run "osm2pgsql --slim --hstore -d tfwm -H localhost -P 5432 -U chris -W west-midlands-latest.osm.pbf" from command line