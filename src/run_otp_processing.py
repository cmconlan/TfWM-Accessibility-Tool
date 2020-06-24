import os
import settings
import csv
import time
import subprocess
import itertools
import multiprocessing
import numpy as np
import pandas as pd
from modeling import open_trip_planner as otp


def get_csv_reader(input_file: str):
    '''Get the CSV reader object for a file'''
    with open(input_file, 'r') as csv_file:
        return csv.reader(otp_trips)


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


def get_total_dist(walk_dist: str, transit_dist: str) -> float:
    return float(walk_dist) + float(transit_dist)


def get_otp_response(host_url, oa_lat, oa_lon, poi_lat, poi_lon, date, time) -> tuple:
    '''Parse the response from OTP into a dict suitable for a Dataframe'''
    response_xml = otp.request_otp(host_url, oa_lat, poi_lat, oa_lon, poi_lon, date, time)
    return otp.parse_response(response_xml, date, time)


def valid_response(response: tuple) -> bool:
    for value in response:
        if value is None:
            return False
    else:
        return True


def write_complete_row(output_csv, completed_row):
    writer = csv.writer(output_csv, delimiter=',')
    writer.writerow(completed_row)


def compute_trips(process_id, host_url, offset, limit, input_file, output_dir):
    output_file = os.path.join(output_dir, f'temp_{process_id}.csv')
    print(f"{process_id} on {host_url} for offset {offset} limit {limit} saving to {output_file}")

    row_counter = 0
    with open(input_file, 'r') as csv_file:
        with open(output_file, 'a', newline='') as output_csv:
            reader = csv.DictReader(csv_file)
            csv_section = get_csv_section(reader, offset, limit)
            for row in csv_section:
                response = get_otp_response(host_url, row['oa_lat'], row['oa_lon'], row['poi_lat'], row['poi_lon'], row['date'], row['time'])
                if valid_response(response):
                    complete_row = (row['trip_id'], *response)
                    write_complete_row(output_csv, complete_row)
                    row_counter += 1
                    if row_counter % 1000 == 0:
                        print(f'Process {process_id} has completed {row_counter} rows. {(row_counter/limit) * 100}% done')
                else:
                    continue
    print(f'{process_id} has completed its chunk.')
    return output_file


def split_trips(input_file: str, output_dir: str) -> None:

    host, port, processes, otps = settings.get_otp_settings()
    processes = int(processes)
    otps = int(otps)
    port = int(port)

    num_trips = num_rows(input_file)
    step_size = get_step_size(num_trips, processes)
    offsets = get_offsets(num_trips, step_size)
    limits = get_limits(processes, step_size)

    hosts = []
    for i in range(processes):
        hosts.append(f"http://{host}:{str(port + (i % otps))}")

    data = np.zeros(shape=(processes, 6), dtype=object)
    # Each row of data[] is passed as input to compute_trips
    data[:, 0] = np.arange(1, processes + 1)  # ID's
    data[:, 1] = hosts
    data[:, 2] = offsets
    data[:, 3] = limits
    data[:, 4] = [input_file] * processes
    data[:, 5] = [output_dir] * processes

    data = data.tolist()

    start = time.time()
    lock = multiprocessing.Lock()
    with multiprocessing.Pool(int(processes)) as pool:
        results = pool.starmap(compute_trips, [tuple(row) for row in data])


    end = time.time()
    elapsed = end - start
    print("{}min elapsed.".format(elapsed / 60.0))
    return results


def combine_complete_files(output_dir, files):
    output_file = open(os.path.join(output_dir, 'results_full_test.csv'), 'w')
    output_csv = csv.writer(output_file)

    for csv_file in files:
        with open(csv_file, newline='') as f:
            reader = csv.reader(f)
            for index, line in enumerate(reader):
                output_csv.writerow(line)


def cleanup(complete_files):
    for f in complete_files:
        os.remove(f)

if __name__ == '__main__':
    settings.load()
    ROOT_FOLDER = settings.get_root_dir()
    input_csv = os.path.join(ROOT_FOLDER, 'data/otp_trips_test.csv')
    output_dir = os.path.join(ROOT_FOLDER, 'results/')

    complete_files = split_trips(input_csv, output_dir)
    combine_complete_files(output_dir, complete_files)
    cleanup(complete_files)
    print("Done!")
