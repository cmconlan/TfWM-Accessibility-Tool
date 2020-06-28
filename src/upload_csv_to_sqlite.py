import os
import argparse
import pandas as pd
import sqlalchemy as db
from settings import load, get_sqlite_settings

DEFAULT_CHUNK_SIZE = 10000                  # How many rows to load per df chunk
SUMMARY_TABLE_NAME = 'otp_results_summary'  # Name of table where OTP results are summarised


def parse_input_args() -> dict:
    '''Parse the input arguments and return a dict keyed by arg names'''
    parser = argparse.ArgumentParser(description='Upload a CSV file to a corresponding table in SQLite')
    parser.add_argument('file', type=str, help='Path to CSV file. The first row is used for column headers')
    parser.add_argument('table', type=str, help='Destination table')
    parser.add_argument('-c', '--chunksize', metavar='chunksize', type=int, default=DEFAULT_CHUNK_SIZE, required=False, 
                        help=f'Number of rows to read per chunk of CSV file to conserve memory. Default: {DEFAULT_CHUNK_SIZE}')
    args = parser.parse_args()
    return vars(args)


def check_input_file_exists(file_name: str) -> None:
    if not os.path.isfile(file_name):
        print(f'Error: File "{file_name}" not found.')
        exit(1)


def create_db_connection() -> db.engine.Engine:
    load() # Load the seetings
    path = get_sqlite_settings()
    return db.create_engine(f'sqlite:///{path}')


def check_table_exists(engine: db.engine.Engine, table: str) -> None:
    if not engine.has_table(table):
        print(f'Error: Table "{table}" not found in the database. Please check the spelling of the destination table name.')
        exit(1)


def copy_text_to_sqlite(input_file: str, table_name: str, engine: db.engine.Engine, chunksize: int = DEFAULT_CHUNK_SIZE) -> None:
    # Read in the input csv chunks at a time to avoid loading large files into memory
    for chunk in pd.read_csv(input_file, chunksize=chunksize):
        chunk.to_sql(table_name, engine, if_exists='replace', index=False)


def create_otp_results_summary(engine: db.engine.Engine, table: str) -> int:
    with engine.connect() as conn:
        conn.execute(f"DELETE FROM {SUMMARY_TABLE_NAME}")
        otp_results_summary = """
        INSERT INTO {summary}
            SELECT
                oa_id,
                poi_type,
                stratum,
                count(*) AS num_trips,
                sum(total_time) AS sum_journey_time,
                sum(walk_dist) AS sum_walking_distance,
                sum(fare) AS sum_fare,
                sum(generalised_cost) AS sum_generalised_cost
            FROM 
                (
                    SELECT 
                        a.*, 
                        b.oa_id, 
                        c.type AS poi_type, 
                        d.stratum,
                        (1.5*(total_time + initial_wait_corrected)
                            - (0.5 * transit_time) 
                            + ((fare * 3600) / 6.7) 
                            + (10 * num_transfers)) / 60 AS generalised_cost
                    FROM 
                        (SELECT *, initial_wait_time - 3600 AS initial_wait_corrected from {results}) AS a 
                        LEFT JOIN otp_trips AS b ON a.trip_id = b.trip_id 
                        LEFT JOIN poi AS c ON b.poi_id = c.poi_id
                        LEFT JOIN trip_strata AS d ON a.trip_id = d.trip_id
                ) AS results_full
            GROUP BY 1,2,3;
        """.format(summary=SUMMARY_TABLE_NAME, results=table)
        result = conn.execute(otp_results_summary)
    return result.rowcount


if __name__ == '__main__':
    args = parse_input_args()
    input_file = args['file']
    table_name = args['table']
    check_input_file_exists(input_file)
    engine = create_db_connection()
    check_table_exists(engine, table_name)
    copy_text_to_sqlite(input_file, table_name, engine, chunksize=args['chunksize'])
    rows_created = create_otp_results_summary(engine, table_name)
    print((
        f'Done!.\n'
        f'File "{input_file}" uploaded to "{table_name}".\n'
        f'{rows_created} rows inserted into {SUMMARY_TABLE_NAME}.'
    ))
