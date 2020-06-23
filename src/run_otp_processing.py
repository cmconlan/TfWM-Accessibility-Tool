import os
import settings
import csv
import time
import subprocess
import itertools
import multiprocessing
import numpy as np
import pandas as pd
from utils import load_yaml, create_connection_from_dict
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


def get_otp_response(host_url, oa_lat, oa_lon, poi_lat, poi_lon, date, time) -> dict:
    '''Parse the response from OTP into a dict suitable for a Dataframe'''
    response = otp.request_otp(host_url, oa_lat, poi_lat, oa_lon, poi_lon, date, time)
    (
        departure_time,
        arrival_time,
        total_time,
        walk_time,
        transfer_wait_time,
        initial_wait_time,
        transit_time,
        walk_dist,
        transit_dist,
        total_dist,
        num_transfers,
        fare
    ) = otp.parse_response(response, date, time)
    response_dict = {
        'departure_time': [departure_time],
        'arrival_time': [arrival_time],
        'total_time': [total_time],
        'walk_time': [walk_time],
        'transfer_wait_time': [transfer_wait_time],
        'initial_wait_time': [initial_wait_time],
        'transit_time': [transit_time],
        'walk_dist': [walk_dist],
        'transit_dist': [transit_dist],
        'total_dist': [total_dist],
        'num_transfers': [num_transfers],
        'fare': [fare]
    }
    return response_dict


def dict_to_df(data_dict, index):
    '''Produce a dataframe from a dict representing OTP results'''
    df = pd.DataFrame(data_dict)
    df.num_transfers = df.num_transfers.astype(pd.Int16Dtype())
    df.set_index(index, inplace=True)
    return df


def compute_trips(process_id, host_url, offset, limit, input_file, output_dir):
    output_file = os.path.join(output_dir, f'results_{process_id}.csv')
    print(f"{process_id} on {host_url} for offset {offset} limit {limit} saving to {output_file}")

    row_counter = 0
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_section = get_csv_section(reader, offset, limit)
        for row in csv_section:
            [oa_id, poi_id, date, time, trip_id, oa_lat, oa_lon, poi_lat, poi_lon] = row
            
            results = get_otp_response(host_url, oa_lat, oa_lon, poi_lat, poi_lon, date, time)
            results['trip_id'] = trip_id
            # Rows are indivually appended to the file to avoid storing many rows in memory
            dict_to_df(results, 'trip_id').to_csv(output_file, index=True, header=False, mode='a')

            row_counter += 1
            if row_counter % 1000 == 0:
                print(f'Process {process_id} has completed {row_counter} rows. {(row_counter/limit) * 100}% done')
    
    print(f'{process_id} has completed its chunk. Saved to {output_file}')


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
    pool = multiprocessing.Pool(int(processes))
    results = pool.starmap(compute_trips, [tuple(row) for row in data])
    pool.close()

    end = time.time()
    elapsed = end - start
    print("Minutes elapsed {}".format(elapsed / 60.0))


if __name__ == '__main__':

    settings.load()
    ROOT_FOLDER = settings.get_root_dir()

    input_csv_name = os.path.join(ROOT_FOLDER, 'data/otp_trips.csv')
    output_dir = os.path.join(ROOT_FOLDER, 'results/')

    otp_data = split_trips(input_csv_name, output_dir)
    print("Done!")
