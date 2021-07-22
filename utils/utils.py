import yaml
import calendar
import holidays
from datetime import datetime, timedelta, date
from itertools import product

def load_yaml(filename: str) -> dict:
    """
     Returns the contents of a yaml file in a list

     Parameters
     ----------
     filename : string
        The full filepath string '.../.../.yaml' of the yaml file to be loaded

     Returns
     -------
     cfg : dict
        Contents of the yaml file (may be a nested dict)
    """
    with open(filename, 'r') as ymlfile:
        cfg = dict(yaml.safe_load(ymlfile))
    return cfg


def load_data_dict(data_config):
    """
    Load mapping information (dictionary) between raw data files to table names in the
    database.

    Parameters
    ----------
    data_config : str
        Path of the config file that stores data dictionaries in yaml.
        This file should contains two dictionaries, one for csv files and one for spatial
        files.

    Returns
    -------
    text_dict : dict
        Data dictionary that maps each raw csv or txt file to its corresponding table name in
        RAW schema of the database, in the form of {'table1.csv': 'table1_alias'}

    gis_dict : dict
        Data dictionary that maps each file directory (containing one .shp file) to its
        corresponding table name in GIS schema of the database, in the form of
        {'dir1': 'dir_alias'}
        
    osm_file : str
        Name of OSM file

    """
    data_dict = load_yaml(data_config)
    text_dict = data_dict['text_dict']
    gis_dict = data_dict['gis_dict']
    osm_file = data_dict['osm_file']
    return text_dict, gis_dict, osm_file


def date_range(start_date, end_date, weekdays=None, exclude_holidays=True):
    """
    Generate a list of all dates within the given period

    Parameters
    ----------
    start_date : datetime.date object
        Starting date of the period
    end_date : datetime.date object
        Ending date of the period
    weekdays : list
        If specified, constrain to these days of the week only, e.g., ['Tuesday', 'Friday']
        
    Returns
    -------
    rng : list
        List of dates in the format of datetime.date
    """
    rng = []
    d = start_date
    while d <= end_date:
        if weekdays is None or list(calendar.day_name)[d.weekday()] in weekdays:
            if not exclude_holidays or d not in holidays.UK():
                rng.append(d)
        d += timedelta(days=1)
    return rng


def time_range(start_time, end_time, unit='m'):
    """
    Generate a list of all timepoints within the given period

    Parameters
    ----------
    start_time : datetime.time object
        Starting time of the period
    end_time : datetime.time object
        Ending date of the period
    unit : string
        Unit of timepoint, supporting hour('h'), minute('m') and second('s')

    Returns
    -------
    rng : list
        List of timepoints in the format of datetime.time object
    """
    unit_dict = {'h': timedelta(hours=1), 'm': timedelta(minutes=1), 's': timedelta(seconds=1)}
    delta = unit_dict[unit]

    rng = []
    t = datetime.combine(date.today(), start_time)
    while t <= datetime.combine(date.today(), end_time):
        rng.append(t.time())
        t += delta
    return rng


def datetime_range(date_range, time_range):
    """
    Generate a list of all combinations of given dates and timepoints

    Parameters
    ----------
    date_range : list of datetime.date object
    time_range : list of datetime.time object

    Returns
    -------
    rng : list of datetime.datetime object
    """
    rng = []
    for (date, time) in product(date_range, time_range):
        rng.append(datetime.combine(date, time))
    return rng
