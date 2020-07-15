import os
import settings
import csv
import time
import itertools
import multiprocessing
import logging
import argparse
import numpy as np
from modeling import open_trip_planner as otp


def parse_input_args() -> dict:
    '''Parse the input arguments and return a dict keyed by arg names'''
    parser = argparse.ArgumentParser(description='Run OTP to compute routes of each trip in the input file')
    parser.add_argument('file', type=str, help='Path to pre-computed trpis CSV file. The first row is used for column headers')
    args = parser.parse_args()
    return vars(args)


def check_input_file_exists(file_name: str) -> None:
    if not os.path.isfile(file_name):
        logging.error(f'File "{file_name}" not found.')
        exit(1)


def get_csv_reader(input_file: str) -> csv.reader:
    '''Get the CSV reader object for a file'''
    with open(input_file, 'r') as csv_file:
        return csv.reader(csv_file)


def num_rows(file_name: str) -> int:
    '''Count the number of rows in the (CSV) file'''
    with open(file_name, 'r') as otp_trips:
        otp_trips_reader = csv.reader(otp_trips)
        rows = sum(1 for row in otp_trips_reader)
    rows -= 1 # Account for the header
    logging.debug(f'{rows} in {file_name}')
    return rows


def get_step_size(num_trips: int, processes: int) -> int:
    '''Calculate how many rows each process will have'''
    return int(np.ceil(num_trips / processes))


def get_csv_section(reader, offset, limit) -> object:
    '''Get a 'slice' or section of the CSV file for a process'''
    return itertools.islice(reader, offset, limit)


def get_otp_response(host_url, input_row) -> tuple:
    '''Parse the response from OTP into tuple of values represnting trip attributes'''
    date = input_row['date']
    time = input_row['time']
    response = otp.request_otp(host_url, input_row)
    trip = otp.parse_response(response)
    if trip:
        trip['trip_id'] = input_row['trip_id']
    return trip


def print_progress_message(process_id:int, row_counter: int):
    rows_complete.value += row_counter
    logging.info((
        f'Process {process_id} has completed {row_counter} rows. '
        f'{(rows_complete.value/num_trips * 100):.2f}% complete'
    ))


def compute_trips(host_url: str, offset: int, limit: int, input_file: str, output_dir: str) -> (str, int):
    """
    Send a request to OTP, parse the response and write a line to the output file.
    Note: Parallel processing begins and ends here - each Python process will run this
    function until it has completed its 'chunk' of data, then it will return the name
    of the file it wrote its data to.
    Recall that individual processes do not share global variables and other data - each 
    process holds a copy of the parent's (process it was created from) data independently 
    of any other process.
    """
    process_id = os.getpid()
    output_file = os.path.join(output_dir, f'temp_{process_id}.csv')
    logging.debug(f"PID {process_id} on {host_url} for range [{offset}, {limit}]\nSaving to: {output_file}")
    bad_rows = 0
    with open(input_file, 'r') as csv_file:
        # Usage of DictReader saves having to unpack rows manually, but
        # requires that the first row of the file has valid, standard headers
        reader = csv.DictReader(csv_file)
        csv_section = get_csv_section(reader, offset, limit)
        # Treat the first row differently because we want to extract
        # CSV headers from the file, allowing us to use DictReader.
        firstRow = next(csv_section)
        first_response = get_otp_response(host_url, firstRow)
        headers = first_response.keys()
        with open(output_file, 'a', newline='') as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=headers, delimiter=',')
            writer.writeheader()
            writer.writerow(first_response)
            row_counter = 1
            for row in csv_section:
                response = get_otp_response(host_url, row)
                # Some trips have None for all attributes due to OTP error or inability to find a trip
                # These trips return 'False' instead of a dict so empty rows are not written to CSV.
                row_counter += 1
                if response:
                    writer.writerow(response)
                else:
                    logging.warning(f'Failed to get OTP response for trip ID: {row["trip_id"]}')
                    bad_rows += 1
                if row_counter % 1000 == 0:
                    print_progress_message(process_id, row_counter)
                    row_counter = 0
    print_progress_message(process_id, row_counter)
    logging.info(f'Process {process_id} has completed its chunk.')
    return output_file, bad_rows


def split_trips(input_file: str, output_dir: str) -> None:

    def init(trips, complete):
        # Make num_trips global in each process.
        # This grants read-only access in compute_trips
        global num_trips
        global rows_complete
        num_trips = trips
        rows_complete = complete

    host, port, processes, otps = settings.get_otp_settings()
    num_trips = num_rows(input_file)
    step_size = get_step_size(num_trips, processes)

    # Distribute processes between OTP addresses in a circular manner.
    # E.g for 4 processes and 2 OTPs, OTP 1 with port 8080 will have 
    # processes 0, 2 while OTP 2 with port 8081 will have processes 1, 3.
    args = []
    for i in range(processes):
        host_url = f"http://{host}:{str(port + (i % otps))}"
        offset =i * step_size
        arg = (
            host_url, 
            offset, 
            min(offset+step_size, num_trips), 
            input_file, 
            output_dir
        )
        args.append(arg)
    # Shared memory int variable to keep track of total rows done
    rows_complete = multiprocessing.Value('i', 0)
    logging.info(f'Using a pool of {processes} workers')
    # Distribute the OTP processing between processes. Each process returns
    # the path to the file it wrote its results to.
    start = time.time()
    with multiprocessing.Pool(int(processes), initializer=init, initargs=(num_trips, rows_complete)) as pool:
        results = pool.starmap(compute_trips, args)
    end = time.time()
    elapsed = end - start
    logging.info(f"{(elapsed / 60.0):.2f} min elapsed.")
    files = []
    bad_rows = 0
    for f, rows in results:
        files.append(f)
        bad_rows += rows
    if bad_rows > 0:
        logging.warning(f"{bad_rows} trips were lost during OTP processing ({(bad_rows/num_trips * 100):.2f}%).")
    return files


def extract_headers(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        return next(reader)


def combine_complete_files(output_dir, files):
    '''Combine the individual files produced by each process into a single main file'''
    output_file_name = os.path.join(output_dir, 'results_full.csv')
    logging.info("Combining results to: " + output_file_name)
    files_iterator = iter(files)
    # Treat the first file differently, so we can extract headers
    first_file = files[0]
    headers = extract_headers(first_file)
    with open(output_file_name, 'w') as output_file:
        output_csv = csv.writer(output_file)
        output_csv.writerow(headers)
        for csv_file in files:
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                for line in reader:
                    output_csv.writerow(line.values())
    return output_file_name


def cleanup(complete_files):
    '''Delete the temp files produced by each process'''
    logging.info("Cleaning up...")
    for f in complete_files:
        os.remove(f)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    settings.load()
    args = parse_input_args()
    # Input CSV MUST HAVE HEADERS - these are included by default by the ETL process
    input_csv = args['file']
    check_input_file_exists(input_csv)
    ROOT_FOLDER = settings.get_root_dir()
    output_dir = os.path.join(ROOT_FOLDER, 'results/')
    complete_files = split_trips(input_csv, output_dir)
    combine_complete_files(output_dir, complete_files)
    cleanup(complete_files)
    logging.info("Done!")
