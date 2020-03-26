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
    with open(input_file, 'r') as csv_file:
        return csv.reader(otp_trips)


def num_rows(file_name: str) -> int:
    print("Counting rows...")
    with open(file_name, 'r') as otp_trips:
        otp_trips_reader = csv.reader(otp_trips)
        rows = sum(1 for row in otp_trips_reader)
    print("Rows:", rows)
    return rows


def get_step_size(num_trips: int, threads: int) -> int:
    return int(np.ceil(num_trips / threads))


def get_offsets(num_trips: int, step_size: int) -> list:
    return np.arange(0, num_trips, step_size)


def get_limits(threads: int, step_size: int) -> list:
    return [step_size] * threads


def get_csv_section(reader, offset, limit) -> object:
    return itertools.islice(reader, offset, offset+limit)


def calculate_fare():
    pass #TODO


def get_otp_response(host_url, oa_lat, oa_lon, poi_lat, poi_lon, date, time) -> dict:
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
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'total_time': total_time,
        'walk_time': walk_time,
        'transfer_wait_time': transfer_wait_time,
        'initial_wait_time': initial_wait_time,
        'transit_time': transit_time,
        'walk_dist': walk_dist,
        'transit_dist': transit_dist,
        'num_transfers': num_transfers,
        'fare': fare
    }
    return response_dict


def dict_to_df(data_dict, index):
    df = pd.DataFrame(data_dict)
    df.num_transfers = df.num_transfers.astype(pd.Int16Dtype())
    df.set_index(index, inplace=True)
    return df


def compute_trips(thread_id, host_url, offset, limit, input_file, output_dir):

    print(f"{thread_id} on {host_url} for offset {offset} limit {limit}")

    results = {
        'trip_id': [],
        'departure_time': [],
        'arrival_time': [],
        'total_time': [],
        'walk_time': [],
        'transfer_wait_time': [],
        'initial_wait_time': [],
        'transit_time': [],
        'walk_dist': [],
        'transit_dist': [],
        'num_transfers': [],
        'fare': []
    }

    row_counter = 0
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_section = get_csv_section(reader, offset, limit)
        for row in csv_section:
            row_counter += 1
            [oa_id, poi_id, date, time, trip_id, oa_lat, oa_lon, poi_lat, poi_lon] = row
            
            for field, value in get_otp_response(host_url, oa_lat, oa_lon, poi_lat, poi_lon, date, time).items():
                results[field].append(value)

            results['trip_id'].append(trip_id)
            if row_counter % 1000 == 0:
                print(f'Process {thread_id} has completed {row_counter} rows. {(row_counter/limit) * 100}% done')
    
    print(f'{thread_id} has completed its chunk. Saving to resuts/results_{thread_id}.csv')
    output_file = os.path.join(output_dir, f'results_{thread_id}.csv')
    dict_to_df(results, 'trip_id').to_csv(output_file, index=True, header=False)


def split_trips(input_file: str, output_dir: str) -> None:

    host, port, threads = settings.get_otp_settings()
    threads = int(threads)

    num_trips = num_rows(input_file)
    step_size = get_step_size(num_trips, threads)
    offsets = get_offsets(num_trips, step_size)
    limits = get_limits(threads, step_size)

    data = np.zeros(shape=(threads, 6), dtype=object)
    # Each row of data[] is passed as input to compute_trips
    data[:, 0] = np.arange(1, threads + 1)  # ID's
    data[:, 1] = [f"http://{host}:{port}"] * threads  # host_urls
    data[:, 2] = offsets  # offsets
    data[:, 3] = limits  # limits
    data[:, 4] = [input_file] * threads
    data[:, 5] = [output_dir] * threads

    data = data.tolist()

    start = time.time()
    pool = multiprocessing.Pool(int(threads))
    results = pool.starmap(compute_trips, [tuple(row) for row in data])
    pool.close()

    end = time.time()
    elapsed = end - start
    print("Minutes elapsed {}".format(elapsed / 60.0))


if __name__ == '__main__':

    settings.load()
    ROOT_FOLDER = settings.get_root_dir()
    host, port, threads = settings.get_otp_settings()

    input_csv_name = os.path.join(ROOT_FOLDER, 'data/otp_trips.csv')
    output_dir = os.path.join(ROOT_FOLDER, 'results/')

    otp_data = split_trips(input_csv_name, output_dir)
    print("Done!")