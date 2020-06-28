import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


def request_otp(host_url, input_row):
    url = host_url + '/otp/routers/default/plan?'
    params = {
        "fromPlace": f"{input_row['oa_lat']},{input_row['oa_lon']}",
        "toPlace": f"{input_row['poi_lat']},{input_row['poi_lon']}",
        "date": f"{input_row['date']}",
        "time": f"{input_row['time']}",
        "mode": "TRANSIT,WALK",
        "arriveBy": "false",
        "numItineraries": "1"
    }
    resp = requests.get(
        url=url,
        params=params,
        headers={'accept': 'application/xml'}
    )
    return resp


def get_request_parameter(node: ET.Element, param: str) -> str:
    request_parameters = node.find('requestParameters')
    return request_parameters.find(param).text


def get_time_from_itinerary(time: str, itinerary):
    dt = datetime.fromtimestamp(float(itinerary.find(time).text) / 1000)
    dt += timedelta(hours=1)
    return dt


def get_total_distance_from_itinerary(itinerary):
    total_dist = 0.0
    for legs in itinerary.findall('legs'):
        if legs.find('legs') is not None:
            for leg in legs.findall('legs'):
                total_dist += float(leg.find('distance').text)
    return total_dist


def get_fare_from_itinerary(itinerary):
    if itinerary.find('fare') is not None:
        fare_obj = itinerary.find('fare')
        if fare_obj.find('details') is not None:
            return float(fare_obj.find('details').find('regular').find('price').find('cents').text) / 100


def calculate_fare(num_transfers, walk_time, total_time):
    if walk_time == total_time:
        return 0.0
    else:
        return 2.40 * (num_transfers + 1)


def validate_trip(trip: dict) -> bool:
    for value in trip.values():
        if value is None:
            return False
    return True


def parse_response(response):
    root = ET.fromstring(response.content)
    trip = {
        'departure_time': None,
        'arrival_time': None,
        'total_time': None,
        'walk_time': None,
        'transfer_wait_time': None,
        'transit_time': None,
        'walk_dist': None,
        'transit_dist': None,
        'total_dist': None,
        'num_transfers': None,
        'initial_wait_time': None,
        'fare': None
    }
    date = get_request_parameter(root, 'date')
    time = get_request_parameter(root, 'time')
    query_time = datetime.strptime(' '.join([date, time]), '%Y-%m-%d %H:%M')
    # Check if there was an error in the OTP response
    trip_valid = False
    if root.find('error').find('msg') is not None:
        # The start and destination were too close, no trip could be found
        if root.find('error').find('message').text in "TOO_CLOSE":
            trip['departure_time'] = query_time
            trip['arrival_time'] = query_time
            trip['total_time'] = 0.0
            trip['walk_time'] = 0.0
            trip['transfer_wait_time'] = 0.0
            trip['transit_time'] = 0.0
            trip['walk_dist'] = 0.0
            trip['transit_dist'] = 0.0
            trip['total_dist'] = 0.0
            trip['num_transfers'] = 0
            trip['initial_wait_time'] = 0.0
            trip['fare'] = 0.0
            trip_valid = True
    else:
        plan = root.find('plan')
        # Go through the iteneraries found in the plan. Should only be 1
        for itineraries in plan.findall('itineraries'):
            if itineraries.find('itineraries') is not None:  # Note that this line discards error XML, where there was no route
                for itinerary in itineraries.findall('itineraries'):
                    format_str = '%Y-%m-%d %H:%M:%S'
                    trip['arrival_time'] = get_time_from_itinerary('endTime', itinerary).strftime(format_str)
                    trip['total_time'] = float(itinerary.find('duration').text)
                    trip['walk_time'] = float(itinerary.find('walkTime').text)
                    trip['transfer_wait_time'] = float(itinerary.find('waitingTime').text)
                    trip['transit_time'] = float(itinerary.find('transitTime').text)
                    trip['walk_dist'] = float(itinerary.find('walkDistance').text)
                    trip['num_transfers'] = int(itinerary.find('transfers').text)
                    trip['total_dist'] = get_total_distance_from_itinerary(itinerary)
                    trip['fare'] = get_fare_from_itinerary(itinerary)
                    if trip['fare'] is None:
                        trip['fare'] = calculate_fare(trip['num_transfers'], trip['walk_time'], trip['total_time'])
                    # capture the wait time before the first bus arrives
                    departure_time = get_time_from_itinerary('startTime', itinerary)
                    trip['initial_wait_time'] = (departure_time - query_time).total_seconds()
                    trip['departure_time'] = departure_time.strftime(format_str)
                    trip['transit_dist'] = trip['total_dist'] - trip['walk_dist']
                    trip_valid = validate_trip(trip)
    if trip_valid:
        return trip
    else:
        return False

if __name__ == '__main__':
    host = "http://localhost:8080"
    test_trip = {
        'oa_lat': 52.4543590421403,
        'oa_lon': -1.81185753550122,
        'poi_lat': 52.43833923,
        'poi_lon': -1.808046699,
        'date': '2020-7-28',
        'time': '07:07'
    }
    faulty_trip = {
        'oa_lat': 52.4493792783661,
        'oa_lon': -1.82771262209541,
        'poi_lat': 52.43833923,
        'poi_lon': -1.808046699,
        'date': '2020-07-28',
        'time': '13:49'
    }
    response = request_otp(host, faulty_trip)
    print(response.content)
    print(parse_response(response, ))
