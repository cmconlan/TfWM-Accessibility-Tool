import sys
sys.path.insert(0, "./www/")

import argparse
import math
import random
import yaml
from typing import Iterable, Set
from datetime import datetime, timedelta
import pandas as pd
import progressbar as pb
from sqlalchemy.sql import text
from www.app import db
from modeling.open_trip_planner import request_otp, parse_response

# Not having the dataclasses module is annoying :(
class OA:

    def __init__(self, oa_id: str, lat: float, lon: float):
        self.oa_id = oa_id
        self.lat = lat
        self.lon = lon


class POI:

    def __init__(self, poi_id: int, lat: float, lon: float):
        self.poi_id = poi_id
        self.lat = lat
        self.lon = lon


class Trip(object):

    def __init__(self, oa: OA, poi: POI, time: datetime):
        self.oa = oa
        self.poi = poi
        self.time = time

    def start_coords(self):
        return self.oa.lat, self.oa.lon

    def destination_coords(self):
        return self.poi.lat, self.poi.lon

    def __repr__(self) -> str:
        return f"<Trip(oa={self.oa.oa_id}, poi={self.poi.poi_id}, time={self.time.timetz()})>"

    def to_dict(self) -> dict:
        return {
            'oa_lat': self.oa.lat,
            'oa_lon': self.oa.lon,
            'poi_lat': self.poi.lat,
            'poi_lon': self.poi.lon,
            'date': str(self.time.date()),
            'time': self.time.strftime("%H:%M")
        }


def sample_random_time(start_interval: datetime, end_interval: datetime):
    time_dif = (end_interval - start_interval)
    minutes_dif = time_dif.seconds // 60
    
    random_mins = random.randrange(0, minutes_dif, 1)
    time_sample = start_interval + timedelta(minutes=random_mins)
    return time_sample


def distance(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    dist = math.sqrt((lat_a-lat_b)**2 + (lon_a-lon_b)**2)
    return dist


def select_oas(oa_ids: Iterable[str]) -> Set[OA]:
    if not oa_ids:
        # If OA IDS is empty, select all of them
        oas = db.engine.execute("SELECT oa_id, oa_lat, oa_lon FROM oa")
    else:
        oa_strs = { f"'{id}'" for id in oa_ids }
        sql_string = "SELECT oa_id, oa_lat, oa_lon FROM oa WHERE oa_id IN (" + ",".join(oa_strs) + ")"
        sql = text(sql_string)
        oas = db.engine.execute(sql)
    return { OA(o.oa_id, o.oa_lat, o.oa_lon) for o in oas }


def select_pois(poi_types: Iterable[str]) -> Set[POI]:
    poi_strs = { f"'{p}'" for p in poi_types }
    sql = text("SELECT poi_id, poi_lat, poi_lon FROM poi WHERE type IN (" + ",".join(poi_strs) + ")")
    pois = db.engine.execute(sql)
    return { POI(p.poi_id, p.poi_lat, p.poi_lon) for p in pois }


def generate_trips(oa_ids: Iterable[str], poi_types: Iterable[str], time_interval_start, time_interval_end) -> Set[Trip]:
    k = 3
    oas = select_oas(oa_ids)
    pois = select_pois(poi_types)

    trips = set()
    for oa in oas:
        k_closest = sorted(pois, key=lambda p: distance(p.lat, p.lon, oa.lat, oa.lon))[0:k]
        for poi in k_closest:
            random_time = sample_random_time(time_interval_start, time_interval_end)
            trip = Trip(oa=oa, poi=poi, time=random_time)
            trips.add(trip)
    return trips


def process_trips(host: str, trips: Set[Trip]):
    results = []
    for trip in pb.progressbar(trips):
        response = request_otp(host, trip.to_dict())
        trip_results = parse_response(response)
        if trip_results:
            results.append(trip_results)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run OTP to compute an access query')
    parser.add_argument('otp-url', type=str, help='The URL of the Open Trip Planner Instance e.g http://localhost:8080')
    parser.add_argument('query-params', type=str, help='Path to the YAML file describe the access query parameters')
    args = vars(parser.parse_args())

    with open(args['query-params']) as yml:
        query_parameters = yaml.safe_load(yml)

    oa_ids = query_parameters['output-areas']
    poi_types = query_parameters['poi-types']
    start_interval_str = query_parameters['time-interval']['start']
    end_interval_str = query_parameters['time-interval']['end']
    start_interval = datetime.strptime(start_interval_str, "%Y-%m-%d %H:%M")
    end_interval = datetime.strptime(end_interval_str, "%Y-%m-%d %H:%M") 


    otp_url = args['otp-url']

    # The google transit feed is currently valid from April 02, 2021 to December 31, 2021
    # so make sure the trips we sample are between those dates
    print("Generating Trips...")
    trips = generate_trips(oa_ids, poi_types, start_interval, end_interval)
    print(f"{len(trips)} trips created.")
    print(f"Sending trips to OTP...")
    results = process_trips(otp_url, trips)
    results_df = pd.DataFrame(results)
    print(results_df)
