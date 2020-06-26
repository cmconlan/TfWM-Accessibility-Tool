import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


def request_otp(host_url, lat_oa, lat_poi, lon_oa, lon_poi, date, time):
    url = host_url + '/otp/routers/default/plan?'
    params = {
        "fromPlace": f"{lat_oa},{lon_oa}",
        "toPlace": f"{lat_poi},{lon_poi}",
        "date": f"{date}",
        "time": f"{time}",
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


def parse_response(response, date, time):
    xml = ET.fromstring(response.content)
    departure_time = None
    arrival_time = None
    total_time = None
    walk_time = None
    transfer_wait_time = None
    transit_time = None
    walk_dist = None
    transit_dist = None
    total_dist = None
    num_transfers = None
    initial_wait_time = None
    fare = None
    query_time = datetime.strptime(' '.join([date, time]), '%Y-%m-%d %H:%M')
    if xml.find('error').find('msg') is not None:
        if xml.find('error').find('message').text in "TOO_CLOSE":
            departure_time = query_time
            arrival_time = query_time
            total_time = 0.0
            walk_time = 0.0
            transfer_wait_time = 0.0
            transit_time = 0.0
            walk_dist = 0.0
            transit_dist = 0.0
            total_dist = 0.0
            num_transfers = 0
            initial_wait_time = 0.0
            fare = 0.0
    else:
        plan = xml.find('plan')
        for itineraries in plan.findall('itineraries'):
            if itineraries.find('itineraries') is not None:  # Note that this line discards error xmls, where there was no route
                for itinerary in itineraries.findall('itineraries'):
                    departure_time = datetime.fromtimestamp(float(itinerary.find('startTime').text) / 1000)
                    departure_time += timedelta(hours=1)
                    arrival_time = datetime.fromtimestamp(float(itinerary.find('endTime').text) / 1000)
                    arrival_time += timedelta(hours=1)
                    total_time = float(itinerary.find('duration').text)
                    walk_time = float(itinerary.find('walkTime').text)
                    transfer_wait_time = float(itinerary.find('waitingTime').text)
                    transit_time = float(itinerary.find('transitTime').text)
                    walk_dist = float(itinerary.find('walkDistance').text)
                    num_transfers = int(itinerary.find('transfers').text)


                    total_dist = get_total_distance_from_itinerary(itinerary)
                    fare = get_fare_from_itinerary(itinerary)
                    if fare is None:
                        fare = calculate_fare(num_transfers, walk_time, total_time)

                    # capture the wait time before the first bus arrives
                    initial_wait_time = (departure_time - query_time).total_seconds()
                    transit_dist = total_dist - walk_dist            

    return departure_time, arrival_time, total_time, walk_time, transfer_wait_time, initial_wait_time, transit_time, walk_dist, transit_dist, total_dist, num_transfers, fare

if __name__ == '__main__':
    pass
