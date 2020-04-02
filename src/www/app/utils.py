from app import app, db
from sqlalchemy import text, exc
from flask import jsonify

def execute_query(sql_string, args=None):
    if args:
        return db.engine.execute(sql_string, *args)
    else:
        return db.engine.execute(sql_string)


def get_json(db_results):
    key_value_pairs = get_key_value_pairs(db_results)
    return jsonify(key_value_pairs)


def get_key_value_pairs(db_results):
    
    def title_case(string):
        first_char = string[0]
        return '_' not in string and first_char == first_char.upper()

    is_list = type(db_results) is list
    pairs = []
    for value in db_results:
        # We either expect RowProxy from SQLAlchemy or a list of strings
        if not is_list:
            (value,) = value

        if not title_case(value):
            pairs.append(key_value_pair(value, humanise(value)))
        else:
            pairs.append(key_value_pair(value, value))
    return pairs


def key_value_pair(key, value):
    return { 'key': key, 'value': value } 


def humanise(string):
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


def remove_common_prefix(strings):
    prefix = find_prefix(strings)
    return [string.replace(prefix, '') for string in strings]


def find_prefix(strs):
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
    if not demographic_groups:
        where_clause = ''
    else:
        where_clause = f'WHERE population IN {construct_where_clause_args(demographic_groups)}'
    query = (f"SELECT oa_id, sum(count) AS pop_count "
            f"FROM populations {where_clause} "
            f"GROUP BY oa_id "
            f"ORDER BY pop_count DESC")
    pairs = []
    results = execute_query(query, demographic_groups)

    return get_metrics(results)


def at_risk_scores(demographics, poi_types, time_strata):
    density = population_density(demographics)
    generalised_score = calculate_access_metric('gen_cost', poi_types, time_strata)
    oa_total = len(density)
    oa_count = 0
    metrics = {}    
    for (oa_id, pop_count) in density.items():
        oa_count += 1
        # We only want at-risk score for the top 50%
        if oa_count <= oa_total // 2:
            metrics[oa_id] = generalised_score[oa_id] / pop_count 
        else:
            break
    return metrics


def calculate_access_metric(access_metric, poi_types, time_strata):
    where_clause = ''
    if poi_types or time_strata:
        where_clause = 'WHERE '
        poi_str = ''
        strata_str = ''
        if poi_types:
            poi_str = 'poi_type IN ' + construct_where_clause_args(poi_types)
        if time_strata:
            strata_str = 'stratum IN ' + construct_where_clause_args(time_strata)

        if poi_str and strata_str:
            where_clause += f'{poi_str} AND {strata_str}'
        else:
            where_clause += poi_str + strata_str
    
    query = (f"SELECT oa_id, sum(sum_{access_metric}) / sum(num_trips) "
            f"FROM otp_results_summary {where_clause} GROUP BY oa_id")
    args = poi_types + time_strata

    try:
        results = execute_query(query, args)
    except exc.SQLAlchemyError as err:
        print(err)
        return {'error': 'Not found'}

    return get_metrics(results)


def construct_where_clause_args(args):
    if type(args) is int:
        num_args = args
    else:
        try:
            num_args = len(args)
        except TypeError:
            raise TypeError("""Supplied object cannot be used to determine number of bind parameters\n
                Value {} is of type {} and has no len()""".format(args, type(args)))

    if num_args == 0:
        return ''
    elif num_args == 1:
        return '(?)'
    else:
        return str(tuple('?' for i in range(num_args))).replace("'", "")


def get_metrics(results):
    return {oa_id: metric for (oa_id, metric) in results}


def add_rank(metrics):
    # Our version fo SQLite doesn't have window functions, so can't use rank()
    # Rank is calculated manually here
    for index, (oa_id, value) in enumerate(sort_by_value(metrics)):
        metrics[oa_id] = {'metric': value, 'rank': index+1}
    return metrics


def sort_by_value(input_dict, reverse=False):
    if type(input_dict) is not dict:
        raise TypeError('Cannot sort a non-dict type by value')

    return sorted(input_dict.items(), key=lambda item: item[1], reverse=reverse)
