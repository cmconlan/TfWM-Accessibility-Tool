import logging
import pandas as pd
import os
from utils.utils import date_range, time_range, datetime_range
from utils.database import Database
from random import seed, sample
from datetime import datetime


def sample_timestamps(time_defs, time_strata, n_timepoints, rseed = 999):
    """
    Sample time points from strata (time segments) and write to MODEL.timestamps
    Example:
        time_seg              |  day         |   time
        +++++++++++++++++++++++++++++++++++++++++++++++
        Weekday inter-peak    |  2019-07-02  |   12:00pm

    Parameters
    ----------
    time_defs : dict
        Definitions of our strata taxonomy, mapping each dimension of the strata to interpretable time strings
        Example:
            {'time_of_day':
                {'peak': ['8:00-9:00'], 'off-peak': ['11:00-15:00']},
            'day_of_week':
                {'weekday': ['Tuesday'], 'saturday': ['Saturday']}}
    
    time_strata : dict
        Dict of strata (time segments), each being a dict of values on foregoing dimensions and the number of
        samples
        Example:
            {'Weekday (AM peak)': {'time_of_day': 'peak', 'day_of_week': 'weekday', 'n_sample': 50}, ...}
    
    n_timepoints : int
        Default number of samples for each stratum, if specified

    rseed : int
        Random seed for random sampling

    Returns
    ----------
    None
    """
    logger = logging.getLogger('root')
    seed(rseed)

    start_date_str = time_defs.get('term')['start_date']
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    end_date_str = time_defs.get('term')['end_date']
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Create list to hold all table rows
    timestamps = []

    # Loop through all strata and create timepoints (at minute level) for each stratum
    for stratum, values in time_strata.items():
        logger.debug(f'Sampling times for "{stratum}"')
        if 'n_sample' in values.keys():
            n = values['n_sample']
        else:
            n = n_timepoints
        time_of_day = time_defs.get('time_of_day')[values['time_of_day']]
        day_of_week = time_defs.get('day_of_week')[values['day_of_week']]

        # All dates in the stratum
        days_in_stratum = date_range(start_date, end_date, day_of_week)

        # All time (minutes) in the stratum
        times_in_stratum = []
        for hours in time_of_day:
            start_time_str, end_time_str = hours.split('-')
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            times_in_stratum += time_range(start_time, end_time)

        # Cartesian product of dates and times -> all time points in the stratum for sampling
        timestamps_in_stratum = datetime_range(days_in_stratum, times_in_stratum)

        # Sample specified number of timepoints
        timestamps_sampled = sample(timestamps_in_stratum, n)

        for ts in timestamps_sampled:
            date = ts.strftime('%Y-%m-%d')
            time = ts.strftime('%H:%M')
            ts_dict = {'stratum': stratum, 'date': date, 'time': time}
            timestamps.append(ts_dict)

    return timestamps

def create_timestamps(time_defs, time_strata, n_timepoints, rseed = 999):
    logger = logging.getLogger('root')
    timestamps = sample_timestamps(time_defs, time_strata, n_timepoints, rseed)
    db = Database.get_instance()
    df = pd.DataFrame(timestamps)
    df.to_sql(f'timestamps', db.engine, schema='model', index=False, if_exists='replace')
    logger.debug(f'Sampled timestamps saved to model.timestamps')

    
def create_k_poi(sql_dir, k_poi, poi_dict):
    """
    For each OA and each type of point of interest (POI), select K nearest spots (by aerial distance) and write the
    results to MODEL.k_poi

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_k_poi.sql

    k_poi : int
        Default # of nearest POIs to compute

    poi_dict : dict
        Keys are POI types as in the "type" column in semantic.poi; for each key, value is the k specific to that
        type, if specified, otherwise use the default k
        Example:
            Hospital: 3
            Job Centre:
    Returns
    ----------
    None
    """
    sql_file = os.path.join(sql_dir, 'create_model_k_poi.sql')

    poi_types = list(poi_dict.keys())
    poi_Ks = [poi_dict[poi] or k_poi for poi in poi_dict]

    params = {'poi_types': str(poi_types), 'poi_Ks': str(poi_Ks)}
    db = Database.get_instance()
    db.execute_sql(sql_file, read_file=True, params=params)
    logging.getLogger('root').debug(f'K nearest POIs saved to model.k_poi')


def create_trips(sql_dir, mode='replace'):
    """
    Configure trip info for each OTP query and save to MODEL.trips

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_trips.sql and append_model_trips.sql

    mode : str
        If 'replace', overwrite existing MODEL.trips; if 'append', append to that existing table

    Returns
    ----------
    None
    """

    if mode == 'replace':
        sql_file = os.path.join(sql_dir, 'create_model_trips.sql')
    if mode == 'append':
        sql_file = os.path.join(sql_dir, 'append_model_trips.sql')
    db = Database.get_instance()
    db.execute_sql(sql_file, read_file=True)
    logging.getLogger('root').debug(f'Trips info saved to MODEL.trips')
    
    
def create_otp_trips(sql_dir, mode='replace'):
    """
    Create dataset to be read into OTP tool

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_trips.sql and append_model_trips.sql

    mode : str
        If 'replace', overwrite existing MODEL.trips; if 'append', append to that existing table

    Returns
    ----------
    None
    """
    db = Database.get_instance()
    sql_file = os.path.join(sql_dir, 'create_model_otp_trips.sql')
    db.execute_sql(sql_file, read_file=True)
    logging.getLogger('root').debug(f'Trips info saved to MODEL.otp_trips')


def compute_populations(sql_dir, populations):
    """
    Compute population statistics, saved to RESULTS.populations
    Example:
           oa  	| population1 | population2
        ++++++++++++++++++++++++++++++++++++
            A	|  	  34      |      28

    Parameters
    ----------
    sql_dir : string
        Directory that stores create_model_trips.sql and append_model_trips.sql
    
    populations : dict
        Dict of populations, where each key is the population name with values being columns in SEMANTIC.oa mapped
        to that population
        Example:
            elderly:
                - age_75_to_84
                - age_85_to_89
            disabled:
                - disability_severe
                - disability_moderate

    Returns
    ----------
    None
    """
    params = {}

    ## Write FEATURE.pop
    pop_col_defs = []
    pop_list = list(populations.keys())
    # get the right column aggregation string for each population
    # e.g. 'COALESCE(disability_severe)+COALESCE(disability_moderate) as disabled'
    for pop in pop_list:
        cols = [f"COALESCE({col}, 0)" for col in populations[pop]]
        pop_col_defs.append('+'.join(cols) + ' as ' + pop)
    # join the strings
    params['pop_col_defs'] = ', '.join(pop_col_defs)

    params['pop_col_names'] = str(pop_list)
    params['pop_cols'] = ', '.join(pop_list)

    sql_file = os.path.join(sql_dir, 'create_results_populations.sql')
    db = Database.get_instance()
    db.execute_sql(sql_file, read_file=True, params=params)
    logging.getLogger('root').debug('OA-level demographics saved to RESULTS.populations')
