from functools import reduce
from app import app, db
from sqlalchemy import text, exc
from flask import jsonify
import math


def execute_query(sql_string, args=None):
    """
    Execute the provided SQL query using the SQLAlchemy Engine.
    If providing positional arguments as `args`, the number of
    positional arguments must match the number of bind parameters
    in the input query string.

    Parameters:
    sql_string (str): A SQL query string
    args (list): List of positional arguments in the same order as 
                 their respective bind parameters

    Returns:
    SQLAlchemy.engine.ResultProxy: The result of the query
    """
    if args:
        return db.engine.execute(sql_string, *args)
    else:
        return db.engine.execute(sql_string)


def get_json(db_results):
    """
    Convert database query results into a JSON string representing a list of key-value pairs

    Parameters:
    db_results (SQLAlchemy.engine.ResultProxy): A ResultProxy (cursor) from SQLAlchemy

    Returns:
    str: JSON string of the form [{'key': key, 'value': value}, ...]
    """
    key_value_pairs = get_key_value_pairs(db_results)
    return jsonify(key_value_pairs)


def get_key_value_pairs(db_results):
    """
    Convert a database query result into a list og key-value pairs, providing
    a human-readable string for the value where possible

    Parameters:
    db_results (SQLAlchemy.engine.ResultProxy): A ResultProxy (cursor) from SQLAlchemy

    Returns:
    list: List of key-value pairs e.g [{'key': key, 'value': value}, ...]
    """
    def snake_case(string):
        """Return True if the provided string is in snake_case"""
        if string:
            first_char = string[0]
            return '_' in string or first_char != first_char.upper()
        else:
            return False

    is_list = type(db_results) is list
    pairs = []
    for value in db_results:
        # We either expect RowProxy from SQLAlchemy or a list of strings
        if not is_list:
            (value,) = value

        if snake_case(value):
            pairs.append(key_value_pair(value, humanise(value)))
        else:
            pairs.append(key_value_pair(value, value))
    return pairs


def key_value_pair(key, value):
    """Return a { 'key': key, 'value': value } dict"""
    return { 'key': key, 'value': value } 


def humanise(string):
    """
    Convert a string from snake_case to Title Case.
    Fully capitalise acronyms such as AM, PM, UK (these are hard-coded)

    Parameters:
    string: str: String to be converted

    Returns:
    str: Title Case form of the input string
    """
    if string:
        string_list = string.split('_')
        return_string = ''
        for substring in string_list:
            if substring in ['am', 'pm', 'uk']:
                return_string += substring.upper()
            else:
                if len(substring) > 1:
                    return_string += substring[0].upper() + substring[1:]
                else:
                    return_string += substring.upper()
            return_string += ' '
        return return_string.strip()
    else:
        return ''


def remove_common_prefix(strings):
    """
    Remove the longest common prefix from a set of strings.
    E.g ['str_one', 'str_two', 'str_three'] will be converted to ['one', 'two', 'three']

    Parameters:
    strings (list): List of strings

    Returns:
    list: List of strings with longest common prefix removed

    Raises:
    ValueError: Exception raised if there is at least one non-string in the list
    """
    all_strings = reduce(lambda x, y: x and y, map(lambda x: type(x) is str, strings))
    if all_strings:
        prefix = find_prefix(strings)
        return [string.replace(prefix, '') for string in strings]
    else:
        raise ValueError('Cannot remove common prefix from a collection of non-strings')


def find_prefix(strs):
    """
    Find the longest common prefix of a collection of strings

    Parameters:
    strs (list): List of strings

    Returns:
    str: The longest common prefix of the input collection of strings
    """
    longest_pre = ""
    if not strs:
        return longest_pre
    shortest_str = min(strs, key=len)
    for i in range(len(shortest_str)):
        if all([x.startswith(shortest_str[:i+1]) for x in strs]):
            longest_pre = shortest_str[:i+1]
        else:
            break
    return longest_pre


def population_density(demographic_groups):
    """
    Calculate the population density metric at OA level for the input demographic groups.
    If no demographic groups are supplied the population density is calculated for
    all groups by default.

    Parameters:
    demographic_groups (list): A list of the demographic groups for which to calculate
                               population density for e.g ['white', 'asian', 'elderly']
    Returns:
    dict: A dictionary keyed by OA ID, with the value being the population density
    """
    if not demographic_groups:
        where_clause = ''
    else:
        where_clause = f'WHERE population IN {construct_in_clause_args(demographic_groups)}'
    query = (f"SELECT oa_id, sum(count) AS pop_count "
            f"FROM populations {where_clause} "
            f"GROUP BY oa_id "
            f"ORDER BY pop_count DESC")
    results = execute_query(query, demographic_groups)

    return get_metrics(results)


def at_risk_scores(demographics, poi_types, time_strata):
    """
    Calculate the at-risk score for an OA given demographic group(s), point-of-interest (POI)
    type(s) and time strata/stratum.
    At-risk score is calculated by dividing the Genralised Access Score by population density
    for the top 50% of OAs based on population density.

    Parameters:
    demographics (list): List of demographic groups as strings.
    poi_types (list): List of POI types as strings.
    time_strata (list): List of Time Strata as strings.

    Returns:
    dict: A dictionary keyed by OA ID, with the value being the at-risk score
    """
    results = execute_query(
        "SELECT oa_id FROM populations WHERE population = 'total' ORDER BY count DESC"
    )
    oa_ids_ordered_by_population = results.fetchall()
    half_number_of_oas = len(oa_ids_ordered_by_population) // 2
    density = population_density(demographics)
    generalised_score = calculate_access_metric('generalised_cost', poi_types, time_strata)

    oa_count = 0
    at_risk_score = {}
    for (oa_id,) in oa_ids_ordered_by_population:
        # We only want at-risk score for the 50% most populated OAs
        if oa_count <= half_number_of_oas:
            if density[oa_id] > 0:
                at_risk_score[oa_id] = generalised_score[oa_id] / density[oa_id] 
            oa_count += 1
        else:
            break
    return at_risk_score


def construct_access_metric_where_clause(poi_types, time_strata):
    """
    Construct a WHERE clause for use querying the otp_results_summary table
    for any given point-of-interest (POI) type(s) and time strata/stratum.
    
    Parameters:
    poi_types (list): List of POI types as strings.
    time_strata (list): List of Time Strata as strings.

    Returns:
    str: a string containing a where clause to be used in a otp_results_summary query
    """
    where_clause = ''
    if poi_types or time_strata:
        where_clause = 'WHERE '
        poi_str = ''
        strata_str = ''
        if poi_types:
            poi_str = 'poi_type IN ' + construct_in_clause_args(poi_types)
        if time_strata:
            strata_str = 'stratum IN ' + construct_in_clause_args(time_strata)

        if poi_str and strata_str:
            where_clause += f'{poi_str} AND {strata_str}'
        else:
            where_clause += poi_str + strata_str

    return where_clause


def calculate_access_metric(access_metric, poi_types, time_strata):
    """
    Calculate an accessibility metric (journey time, walking distance, fare, generalised access score)
    for OAs given point-of-interest (POI) type(s) and time strata/stratum.
    
    Parameters:
    access_metric (str): The accessibility metric to calculate.
    poi_types (list): List of POI types as strings.
    time_strata (list): List of Time Strata as strings.

    Returns:
    dict: A dictionary keyed by OA ID, with the value being the accessibility metric.
          Will return 404 if the access metric supplied doesn't exist in the database
    """
    where_clause = construct_access_metric_where_clause(poi_types, time_strata)

    query = (f"SELECT oa_id, sum(sum_{access_metric}) / sum(num_trips) "
             f"FROM otp_results_summary {where_clause} GROUP BY oa_id")
    args = poi_types + time_strata

    try:
        results = execute_query(query, args)
    except exc.SQLAlchemyError as err:
        print(err)
        return {'error': 'Not found'}

    return get_metrics(results)


def calculate_high_level_metrics(access_metric, poi_types, time_strata):
    """
    Calculate a high level accessibility metric (journey time, walking distance, fare, generalised access score)
    for all OAs given point-of-interest (POI) type(s) and time strata/stratum.
    
    Parameters:
    access_metric (str): The accessibility metric to calculate.
    poi_types (list): List of POI types as strings.
    time_strata (list): List of Time Strata as strings.

    Returns:
    dict: A dictionary keyed by metric type, with the value being the value of the metric.
          Will return a dict with the key 'error' if the access metric supplied doesn't exist in the database
    """
    where_clause = construct_access_metric_where_clause(poi_types, time_strata)
    args = poi_types + time_strata

    try:
        query = (f"SELECT sum(sum_{access_metric}) as summation_a, \
                   sum(sum_of_squared_{access_metric}) as summation_of_squared_a, \
                   sum(num_trips) as n \
                   FROM otp_results_summary {where_clause}")
        i_vals = get_metric_with_fields(execute_query(query, args))  # (i_vals = intermediate values)

        mean = i_vals['summation_a'] / i_vals['n']
        return {
            'Mean': round(mean, 2),
            'Variance': round(math.sqrt((i_vals['summation_of_squared_a'] - 2 * mean * i_vals['summation_a'] + i_vals['n'] * (mean ** 2)) / (i_vals['n'] - 1)), 2),
            'Jains Index': round((i_vals['summation_a'] ** 2) / (i_vals['n'] * i_vals['summation_of_squared_a']), 3)
        }
    except exc.SQLAlchemyError as err:
        print(err)
        return {'error': f"High level metric calculation error: {err}"}


def calculate_demographic_level_metrics(access_metric, poi_types, time_strata):
    """
    Calculate a demographic level accessibility metrics (journey time, walking distance, fare, generalised access score)
    for all demographics given point-of-interest (POI) type(s) and time strata/stratum.
    
    Parameters:
    access_metric (str): The accessibility metric to calculate.
    poi_types (list): List of POI types as strings.
    time_strata (list): List of Time Strata as strings.

    Returns:
    dict: A dictionary keyed by demographic, with the value being a dictionary of metrics.
          Will return a dict with the key 'error' if an error occurs in the calculation
    """
    where_clause = construct_access_metric_where_clause(poi_types, time_strata)
    args = poi_types + time_strata

    try:
        query = f"SELECT populations.population, \
                    sum(populations.count) as sum_d, \
                    sum(stats.sum_of_metric * populations.count) as sum_a_d, \
                    sum(stats.sum_of_metric * populations.count * stats.sum_of_metric * populations.count) as sum_of_squared_a_d, \
                    sum(stats.n) as n    \
                        \
                FROM(SELECT \
                        oa_id, \
                        sum(sum_{access_metric}) / sum(num_trips) as sum_of_metric, \
                        count(*) as n \
                        FROM otp_results_summary {where_clause} \
                        GROUP BY oa_id \
                    ) stats \
                        \
                LEFT JOIN populations \
                ON populations.oa_id = stats.oa_id \
                GROUP BY populations.population"

        db_results = execute_query(query, args)
        fieldNames = db_results.keys()
        result = {
            fields[0]: {
                list(fieldNames)[idx]: field for (idx, field) in enumerate(fields)
            } 
            for fields in db_results
        }

        for demographic in result:
            i_vals = result[demographic]  # (i_vals = intermediate values)
            result[demographic] = {
                'WASS': round(i_vals['sum_a_d'] / i_vals['sum_d'], 2),
                'JI': round((i_vals['sum_a_d'] ** 2) / (i_vals['n'] * i_vals['sum_of_squared_a_d']), 3)
            }

        mean = result['total']['WASS']
        del result['total']
        for demographic in result:
            result[demographic]['ARM'] = round(result[demographic]['WASS'] - mean, 2)

        return result
    except exc.SQLAlchemyError as err:
        print(err)
        return {'error': f"High level metric calculation error: {err}"}


def construct_in_clause_args(args):
    """
    Produce a string containing bind parameters ('?') to be used in a `WHERE column IN ()` clause.
    The number of bind parameters is supplied as an `int` or extracted from the length of the
    supplied `args` collection (must have len()).

    Parameters:
    args (int): Number of bind parameters to create. If args is a collection, its length is used.

    Returns:
    str: a string containing n bind parameters, where n is equal to args or len(args)

    Raises:
    TypeError: Excpetion raised if the supplied collection does not have a len()
    """
    if type(args) is int:
        if args < 0:
            raise ValueError('Number of arguments must be non-negative')
        num_args = args
    else:
        num_args = get_object_length(args)

    if num_args == 0:
        return '()'
    elif num_args == 1:
        return '(?)'
    else:
        return str(tuple('?' for i in range(num_args))).replace("'", "")


def get_object_length(obj):
    try:
        return len(obj)
    except TypeError:
        raise TypeError("Value {} has no len()".format(obj))


def get_metrics(db_results):
    """
    Produce a dict of the form {oa_id: metric} from the result of a database query.

    Parameters:
    db_results (SQLAlchemy.engine.ResultProxy): A ResultProxy (cursor) from SQLAlchemy.

    Returns:
    dict: A dictionary keyed by OA ID, with the value being the metric value
    """
    return {oa_id: metric for (oa_id, metric) in db_results}


def get_metric_with_fields(db_results):
    """
    Produce a dict of the form {field: value} from the result of a database query.

    Parameters:
    db_results (SQLAlchemy.engine.ResultProxy): A ResultProxy (cursor) from SQLAlchemy.

    Returns:
    dict: A dictionary keyed by the field name from the query, with the value being the first value of the field
    """
    fieldNames = db_results.keys()
    fieldValues = list(db_results)[0]
    return {list(fieldNames)[i]: fieldValues[i] for i in range(0, len(fieldNames))}


def add_rank(metrics):
    """
    Rank the OA metrics by metric value
    i.e the lowest metric value has rank 1, next lowest rank 2 etc.

    Parameters:
    metrics (dict): A dictionary keyed by OA ID, with the value being the metric value

    Returns:
    dict: A dictionary keyed by OA ID, with the value being a dictionary of the form {'rank': x, 'metric' y}
    """
    # Our version of SQLite doesn't have window functions, so can't use rank(). 
    # Rank is calculated manually here.
    for index, (oa_id, value) in enumerate(sort_by_value(metrics)):
        metrics[oa_id] = {'metric': value, 'rank': index+1}
    return metrics


def sort_by_value(input_dict, reverse=False):
    """
    Sort a dictionary by returning an iterator of
    the dictionary items in order of its values.

    Parameters:
    input_dict (dict): dictionary with sort-able values.
    reverse (bool): Set to True to return items in descending order of values.

    Returns:
    iterator: An iterator that returns (key, value) tuples of the input dictionary
              in order of the values.

    Raises:
    TypeError: Exception raised of the value is not a dictionary
    """
    if type(input_dict) is not dict:
        raise TypeError('Cannot sort a non-dict type by value')

    return sorted(input_dict.items(), key=lambda item: item[1], reverse=reverse)
