import pytest
from app.utils import *


def test_get_key_value_pairs():
    pairs =  get_key_value_pairs(['string_one'])
    unchanged_pairs = get_key_value_pairs(['String two'])
    assert pairs == [{'key': 'string_one', 'value': 'String One'}]
    assert get_key_value_pairs([]) == []
    assert get_key_value_pairs(['']) == [{'key': '', 'value': ''}]
    assert unchanged_pairs == [{'key': 'String two', 'value': 'String two'}]


def test_humanise():
    assert humanise('all') == 'All'
    assert humanise('white') == 'White'
    assert humanise('asian_indian') == 'Asian Indian'
    assert humanise('PerfectlyNormal') == "PerfectlyNormal"
    assert humanise('') == ''
    assert humanise(None) == ''


def test_key_value_pair():
    assert key_value_pair('Hello', 'World') == {'key': 'Hello', 'value': 'World'}
    assert key_value_pair('', '') == {'key': '', 'value': ''}
    assert key_value_pair(None, None) == {'key': None, 'value': None}


def test_remove_common_prefix():
    strings_with_common_prefix = ['hello_world', 'hello_sunshine', 'hello_is_it_me_youre_looking_for']
    strings_without_common_prefix = ['hello', 'world', 'python']
    not_strings = [None, 123, []]
    assert remove_common_prefix(strings_with_common_prefix) == ['world', 'sunshine', 'is_it_me_youre_looking_for']
    assert remove_common_prefix(strings_without_common_prefix) == strings_without_common_prefix
    with pytest.raises(ValueError) as e_info:
        remove_common_prefix(not_strings)


def test_find_prefix():
    strings_with_common_prefix = ['hello_world', 'hello_sunshine', 'hello_is_it_me_youre_looking_for']
    strings_without_common_prefix = ['hello', 'world', 'python']
    assert find_prefix(strings_with_common_prefix) == 'hello_'
    assert find_prefix(strings_without_common_prefix) == ''
    assert find_prefix([]) == ''
    assert find_prefix(None) == ''


def test_construct_in_clause_args():
    list_args = [1, 2, 3]
    tuple_args = (4, 6, 7)
    dict_args = {'a': 1, 'b': 2, 'c': 3}
    assert construct_in_clause_args(0) == '()'
    assert construct_in_clause_args(1) == '(?)'
    assert construct_in_clause_args(3) == '(?, ?, ?)'
    assert construct_in_clause_args([1]) == '(?)'
    assert construct_in_clause_args(list_args) == '(?, ?, ?)'
    assert construct_in_clause_args(tuple_args) == '(?, ?, ?)'
    assert construct_in_clause_args(dict_args) == '(?, ?, ?)'
    with pytest.raises(ValueError) as ve:
        construct_in_clause_args(-1)
    with pytest.raises(TypeError) as e_info:
        construct_in_clause_args(None)


def test_add_rank():
    example_ranks = {
        'E001' : {
            'metric': 0,
            'rank': 1
        },
        'E002' : {
            'metric': 5,
            'rank': 2
        },
        'E003' : {
            'metric': 10,
            'rank': 3
        },
    }
    example_metrics = {
        'E001' : 0,
        'E003' : 10,
        'E002' : 5,
    }
    assert add_rank(example_metrics) == example_ranks
    assert add_rank({}) == {}
    assert add_rank({'E001': 1}) == {'E001': { 'metric': 1, 'rank': 1 }}
    with pytest.raises(TypeError) as e_info:
        add_rank(None)
        add_rank([])


def test_sort_by_value():
    example_metrics = {
        'E001' : 0,
        'E003' : 10,
        'E002' : 5,
    }
    expected_order = [('E001', 0), ('E002', 5), ('E003', 10)]
    assert list(sort_by_value(example_metrics)) == expected_order
