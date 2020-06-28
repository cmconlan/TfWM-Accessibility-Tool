import os
import settings
import csv
import time
import itertools
import multiprocessing
import numpy as np
from modeling import open_trip_planner as otp


def get_csv_reader(input_file: str) -> csv.reader:
    '''Get the CSV reader object for a file'''
    with open(input_file, 'r') as csv_file:
        return csv.reader(csv_file)


def num_rows(file_name: str) -> int:
    '''Count the number of rows in the (CSV) file'''
    print("Counting rows...")
    with open(file_name, 'r') as otp_trips:
        otp_trips_reader = csv.reader(otp_trips)
        rows = sum(1 for row in otp_trips_reader)
    print("Rows:", rows)
    return rows


def get_step_size(num_trips: int, processes: int) -> int:
    '''Calculate how many rows each process will have'''
    return int(np.ceil(num_trips / processes))


def get_offsets(num_trips: int, step_size: int) -> list:
    '''
    Calculate the row offsets for each process such that all
    processes have pairwise disjoint sets of rows
    '''
    return np.arange(0, num_trips, step_size)


def get_limits(processes: int, step_size: int) -> list:
    '''Get the max row number each process should go up to'''
    return [step_size] * processes


def get_csv_section(reader, offset, limit) -> object:
    '''Get a 'slice' or section of the CSV file for a process'''
    return itertools.islice(reader, offset, offset+limit)


def get_otp_response(host_url, input_row) -> tuple:
    '''Parse the response from OTP into tuple of values represnting trip attributes'''
    date = input_row['date']
    time = input_row['time']
    response = otp.request_otp(host_url, input_row)
    trip = otp.parse_response(response)
    if trip:
        trip['trip_id'] = input_row['trip_id']
    return trip


def valid_response(response: tuple) -> bool:
    for value in response:
        if value is None:
            return False
    else:
        return True


def compute_trips(process_id: int, host_url: str, offset: int, limit: int, input_file: str, output_dir: str) -> str:
    """
    Send a request to OTP, parse the response and write a line to the output file.
    Note: Parallel processing begins and ends here - each Python process will run this
    function until it has completed its 'chunk' of data, then it will return the name
    of the file it wrote its data to.
    Recall that individual processes do not share global variables and other data - each 
    process holds a copy of the parent's (process it was created from) data independently 
    of any other process.
    """
    output_file = os.path.join(output_dir, f'temp_{process_id}.csv')
    print(f"{process_id} on {host_url} for offset {offset} limit {limit} saving to {output_file}")

    row_counter = 0
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
            for row in csv_section:
                response = get_otp_response(host_url, row)
                # Some trips have None for all attributes due to OTP error or inability to find a trip
                # These trips return 'False' instead of a dict so empty rows are not written to CSV.
                if response:
                    writer.writerow(response)
                    row_counter += 1
                    if row_counter % 1000 == 0:
                        print((
                            f'Process {process_id} has completed {row_counter} rows. '
                            f'{((row_counter/limit) * 100):.2f}% for this process'
                        ))

    print(f'{process_id} has completed its chunk.')
    return output_file


def split_trips(input_file: str, output_dir: str) -> None:
    host, port, processes, otps = settings.get_otp_settings()
    num_trips = num_rows(input_file)
    step_size = get_step_size(num_trips, processes)
    offsets = get_offsets(num_trips, step_size)
    limits = get_limits(processes, step_size)

    # Distribute processes between OTP addresses in a circular manner.
    # E.g for 4 processes and 2 OTPs, OTP 1 with port 8080 will have 
    # processes 0, 2 while OTP 2 with port 8081 will have processes 1, 3.
    hosts = []
    for i in range(processes):
        hosts.append(f"http://{host}:{str(port + (i % otps))}")

    data = np.zeros(shape=(processes, 6), dtype=object)
    # Each row of data[] is a set of arguments to compute_trips
    data[:, 0] = np.arange(1, processes + 1)  # Process ID's
    data[:, 1] = hosts
    data[:, 2] = offsets
    data[:, 3] = limits
    data[:, 4] = [input_file] * processes
    data[:, 5] = [output_dir] * processes
    data = data.tolist()

    start = time.time()
    # Distribute the OTP processing between processes. Each process returns
    # the path to the file it wrote its results to.
    with multiprocessing.Pool(int(processes)) as pool:
        results = pool.starmap(compute_trips, [tuple(row) for row in data])
    end = time.time()
    elapsed = end - start
    print(f"{(elapsed / 60.0):.2f}min elapsed.")
    return results


def extract_headers(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        return next(reader)


def combine_complete_files(output_dir, files):
    '''Combine the individual files produced by each process into a single main file'''
    output_file_name = os.path.join(output_dir, 'results_full.csv')
    print("Combining results to: " + output_file_name)
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


def cleanup(complete_files):
    '''Delete the temp files produced by each process'''
    print("Cleaning up...")
    for f in complete_files:
        os.remove(f)


if __name__ == '__main__':
    settings.load()
    ROOT_FOLDER = settings.get_root_dir()
    # Input CSV MUST HAVE HEADERS - these are included by default by the ETL process
    input_csv = os.path.join(ROOT_FOLDER, 'data/otp_trips_test.csv')
    output_dir = os.path.join(ROOT_FOLDER, 'results/')
    complete_files = split_trips(input_csv, output_dir)
    combine_complete_files(output_dir, complete_files)
    cleanup(complete_files)
    print("Done!")
