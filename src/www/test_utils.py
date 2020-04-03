import pytest
import app.utils as utils


def test_get_key_value_pairs():
    pairs =  utils.get_key_value_pairs(['string_one'])
    unchanged_pairs = utils.get_key_value_pairs(['String two'])
    assert pairs == [{'key': 'string_one', 'value': 'String One'}]
    assert utils.get_key_value_pairs([]) == []
    assert utils.get_key_value_pairs(['']) == [{'key': '', 'value': ''}]
    assert unchanged_pairs == [{'key': 'String two', 'value': 'String two'}]


def test_humanise():
    assert utils.humanise('all') == 'All'
    assert utils.humanise('white') == 'White'
    assert utils.humanise('asian_indian') == 'Asian Indian'
    assert utils.humanise('PerfectlyNormal') == "PerfectlyNormal"
    assert utils.humanise('') == ''
    assert utils.humanise(None) == ''


def test_key_value_pair():
    assert utils.key_value_pair('Hello', 'World') == {'key': 'Hello', 'value': 'World'}
    assert utils.key_value_pair('', '') == {'key': '', 'value': ''}
    assert utils.key_value_pair(None, None) == {'key': None, 'value': None}


def test_remove_common_prefix():
    strings_with_common_prefix = ['hello_world', 'hello_sunshine', 'hello_is_it_me_youre_looking_for']
    strings_without_common_prefix = ['hello', 'world', 'python']
    not_strings = [None, 123, []]
    assert utils.remove_common_prefix(strings_with_common_prefix) == ['world', 'sunshine', 'is_it_me_youre_looking_for']
    assert utils.remove_common_prefix(strings_without_common_prefix) == strings_without_common_prefix
    with pytest.raises(ValueError) as e_info:
        utils.remove_common_prefix(not_strings)


def test_find_prefix():
    strings_with_common_prefix = ['hello_world', 'hello_sunshine', 'hello_is_it_me_youre_looking_for']
    strings_without_common_prefix = ['hello', 'world', 'python']
    assert utils.find_prefix(strings_with_common_prefix) == 'hello_'
    assert utils.find_prefix(strings_without_common_prefix) == ''
    assert utils.find_prefix([]) == ''
    assert utils.find_prefix(None) == ''


def test_construct_in_clause_args():
    list_args = [1, 2, 3]
    tuple_args = (4, 6, 7)
    dict_args = {'a': 1, 'b': 2, 'c': 3}
    assert utils.construct_in_clause_args(0) == '()'
    assert utils.construct_in_clause_args(1) == '(?)'
    assert utils.construct_in_clause_args(3) == '(?, ?, ?)'
    assert utils.construct_in_clause_args([1]) == '(?)'
    assert utils.construct_in_clause_args(list_args) == '(?, ?, ?)'
    assert utils.construct_in_clause_args(tuple_args) == '(?, ?, ?)'
    assert utils.construct_in_clause_args(dict_args) == '(?, ?, ?)'
    with pytest.raises(ValueError) as ve:
        utils.construct_in_clause_args(-1)
    with pytest.raises(TypeError) as e_info:
        utils.construct_in_clause_args(None)


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
    assert utils.add_rank(example_metrics) == example_ranks
    assert utils.add_rank({}) == {}
    assert utils.add_rank({'E001': 1}) == {'E001': { 'metric': 1, 'rank': 1 }}
    with pytest.raises(TypeError) as e_info:
        utils.add_rank(None)
        utils.add_rank([])


def test_sort_by_value():
    example_metrics = {
        'E001' : 0,
        'E003' : 10,
        'E002' : 5,
    }
    expected_order = [('E001', 0), ('E002', 5), ('E003', 10)]
    assert list(utils.sort_by_value(example_metrics)) == expected_order
