'''
Wrapper for a singleton SQLAlchemy engine 
instance which adds extra ETL functionality.
'''
import logging
import os
import settings
import subprocess
import pandas as pd
import sqlalchemy as db
import progressbar as pb
from pathlib import Path

class Database:

    _instance = None

    @classmethod
    def get_instance(cls) -> None:
        if Database._instance is None:
            _instance = Database(cls)
        return _instance

    def __init__(self, cls):
        if cls == Database:
            credentials = settings.get_psql()
            db_url = db.engine.url.URL(
                drivername='postgresql',
                username=credentials['user'], 
                password=credentials['password'],
                host=credentials['host'],
                database=credentials['dbname'],
                port=credentials['port']
            )
            self._credentials = credentials
            self.engine = db.create_engine(db_url, echo=False)
        else:
            raise AssertionError(
                    "Database can only be created using get_instance")

    def copy_text_to_db(self, src_file: str, dst_table: str, header=True, sep=',') -> None:
        """
        Copy a csv or txt file to a specified database, where the corresponding table has been created
        Parameters
        ----------
        src_file : str
            Path of the source csv file to be copied
        dst_table : str
            Full name of the database table that stores the .csv file , in the form of "schema.table"
        header: boolean
            Whether the csv file has column names in the first row
        sep : str
            File delimiter
        
        Returns
        -------
        None
        """
        conn = self.engine.raw_connection()
        try:
            cursor = conn.cursor()
            with open(src_file, 'r', encoding='ISO-8859-1') as f:
                if header:
                    head = 'HEADER'
                else:
                    head = ''
                cursor.copy_expert(f"COPY {dst_table} FROM STDIN with DELIMITER '{sep}' {head} CSV", f)
                conn.commit()
                logging.getLogger('root').debug(f"{src_file} copied to {dst_table}")
        finally:
            conn.close()

    def copy_table_to_csv(self, src_table: str, dst_file: str):
        conn = self.engine.raw_connection()
        try:
            cursor = conn.cursor()
            copy_statement = f"COPY (SELECT * FROM {src_table}) TO STDOUT WITH CSV HEADER"
            with open(dst_file, 'w') as csv_file:
                cursor.copy_expert(copy_statement, csv_file)
            cursor.close()
        finally:
            conn.close()
    
    def load_shp_to_db(self, src_dir, dst_table):
        """
        Load shapefiles to database

        Parameters
        ----------
        src_dir : str
            Directory where GIS file directories (each containing one .shp file only) are stored locally
        
        dst_table: str
            Full name of the database table that stores the .shp file , in the form of "schema.table"
        Returns
        -------
        None
        """
        # Must be INSIDE the same directory as the .shp file in order to pull other files
        # Go into each directory and get the shapefile
        os.chdir(src_dir)
        logger = logging.getLogger('root')
        for source, dirs, files in os.walk(src_dir):
            for file in files:
                if file[-3:] == 'shp':
                    shapefile = file
                    command = (
                        f"shp2pgsql -I -s 4326 -d {shapefile} {dst_table}"
                        f" | psql -q -U {self._credentials['user']} -d {self._credentials['dbname']}"
                    )
                    logger.info(f"Uploading {shapefile}")
                    # Using shell=True is bad, but will have to do while 
                    # command-line utilities for PostGIS are only available
                    # from system PATH
                    command_output = subprocess.check_output(command, shell=True, text=True)
                    logger.debug(command_output)

    def load_osm_to_db(self, DATA_DIR, src_file, sql_file):
        """
        Load OpenStreetMap data to database

        Parameters
        ----------
        DATA_DIR : str
            Directory where raw data are stored locally
        src_file : str
            Name of .pbf file
        sql_file : str
            Name of SQL file for updating OSM data

        Returns
        -------
        None

        """
        os.chdir(DATA_DIR)
        logger = logging.getLogger('root')
        # Use osm2pgsql to upload OSM data to the PUBLIC schema
        # This command can fail if default.style is not in DATA_DIR
        command = (
            f"osm2pgsql --slim --hstore -d {self._credentials['dbname']}"
            f" -H {self._credentials['host']} -P {self._credentials['port']}"
            f" -U {self._credentials['user']} {src_file}"
        )
        logger.info(f"Uploading file {src_file} using osm2pgsql")
        try:
            osm_porcess =  subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True
            )
            with osm_porcess.stdout as pipe:
                for line in iter(pipe.readline):
                    logger.info(line)
        except subprocess.SubprocessError as e:
            logger.error('osm2pgsql failed. Check logs for details.')
            logger.debug(e)
            exit(1)
        # Rename the files and move to RAW schema
        self.execute_sql(sql_file, read_file=True)

    def load_text(self, DATA_DIR, data_dict):
        """
        Load csv or txt files to database

        Parameters
        ----------
        DATA_DIR : str
            Directory where the raw data are stored locally
        
        data_dict: str
            Data dictionary that maps each raw csv or txt file to its corresponding table name in
            RAW schema of the database, in the form of {'table1.csv': 'table1_alias'}
        Returns
        -------
        None
        """
        for textfile in pb.progressbar(data_dict.keys()):

            infile = os.path.join(DATA_DIR, textfile)
            outtable = 'raw.' + data_dict[textfile]

            if textfile.endswith('.csv'):
                sep = ','
            elif textfile.endswith('.txt'):
                sep = ','
            # for some reason even these text files only worked uploading with ',' delimiter
            self.copy_text_to_db(src_file=infile, dst_table=outtable, sep=sep)


    def load_gis(self, DATA_DIR, data_dict):
        """
        Load gis (shape) files to database

        Parameters
        ----------
        DATA_DIR : str
            Directory where the raw data are stored locally
        
        data_dict: dict
            Data dictionary that maps each file directory (containing one .shp file) to its 
            corresponding table name in GIS schema of the database, in the form of
            {'dir1': 'dir_alias'}

        Returns
        -------
        None
        """
        for dir in data_dict.keys():
            indir = os.path.join(DATA_DIR, dir)
            outtable = 'gis.' + data_dict[dir]
            self.load_shp_to_db(indir, outtable)

    def execute_sql(self, string, read_file, return_df=False, chunksize=None, params=None):
        """
        Executes a SQL query from a file or a string using SQLAlchemy engine
        Note: Must only be basic SQL (e.g. does not run PSQL \copy and other commands)
        Note: SQL file CANNOT START WITH A COMMENT! There can be comments later on in the file, but for some reason
        doesn't work if you start with one (seems to treat the entire file as commented)

        Parameters
        ----------
        string : string
            Either a filename (with full path string '.../.../.sql') or a specific query string to be executed
            Can include "parameters" (in the form of {param_name}) whose values are filled in at the time of execution
        read_file : boolean
            Whether to treat the string as a filename or a query
        print_ : boolean
            Whether to print the 'Executed query' statement
        return_df : boolean
            Whether to return the result table of query as a Pandas dataframe
        chunksize : int
            Rows will be read in batches of this size at a time; all rows will be read at once if not specified
        params : dict
            In the case of parameterized SQL, the dictionary of parameters in the form of {'param_name': param_value}

        Returns
        -------
        ResultProxy : ResultProxy
            see SQLAlchemy documentation; results of query
        """
        if read_file:
            query = Path(string).read_text()
        else:
            query = string

        if params is not None:
            query = query.format(**params)

        if return_df:
            res_df = pd.read_sql_query(query, self.engine, chunksize=chunksize)
            return res_df
        else:  # Not all result objects return rows.
            self.engine.execute(query)
