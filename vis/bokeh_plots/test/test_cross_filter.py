import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest

from ..cross_filter import (parse_es_response, calculate_query_correlation,
    calculate_graph_coords, duplicate_multi_rows, normalize)

@pytest.fixture
def es_response():
    return [
        {u'query': [u'apple', u'banana'],
         u'retrieved': [u'2016-04-16T00:06:35.292'],
         u'tag': [u'Relevant'],
         u'url': [u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937']},
        {u'query': [u'apple', u'banana'],
         u'retrieved': [u'2016-04-16T00:06:36.135'],
         u'tag': [u'Irrelevant', u'Relevant'],
         u'url': [u'http://www.applevacations.com/']},
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:34.806'],
         u'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU']},
        {u'query': [u'banana'],
         u'retrieved': [u'2016-04-16T00:06:36.135'],
         u'tag': [u'Irrelevant', u'Relevant'],
         u'url': [u'http://www.bananavacations.com/']},
        {u'query': [u'carrot'],
         u'retrieved': [u'2016-04-16T00:06:34.806'],
         u'url': [u'http://www.nytimes.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU']}
    ]


def test_parse_es_response(es_response):
    # note that data becomes ordered by `retrieved` field
    data = {'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU',
             u'http://www.nytimes.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU',
             u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937',
             u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937',
             u'http://www.applevacations.com/',
             u'http://www.applevacations.com/',
             u'http://www.applevacations.com/',
             u'http://www.applevacations.com/',
             u'http://www.bananavacations.com/',
             u'http://www.bananavacations.com/'],
     'query': [u'apple', u'carrot', u'apple', u'banana', u'apple', u'apple', u'banana', u'banana', u'banana', u'banana'],
     'tag': ['Untagged', 'Untagged', u'Relevant', u'Relevant', u'Irrelevant', u'Relevant', u'Irrelevant', u'Relevant', u'Irrelevant', u'Relevant'],
     'hostname': [u'reuters.com', u'nytimes.com', u'politico.com', u'politico.com', u'applevacations.com', u'applevacations.com', u'applevacations.com', u'applevacations.com', u'bananavacations.com', u'bananavacations.com'],
     'tld': [u'.com', u'.com', u'.com', u'.com', u'.com', u'.com', u'.com', u'.com', u'.com', u'.com']}

    df = parse_es_response(es_response)

    assert df.to_dict('list') == data
    assert df.index.tz.tzname("") == 'UTC'

def test_calculate_query_correlation(es_response):
    df = parse_es_response(es_response)

    graph = calculate_query_correlation(df, 'query')

    assert graph == {(u'apple', u'banana'): 1.0}

def test_calculate_graph_coords(es_response):
    df = parse_es_response(es_response)

    graph = calculate_graph_coords(df, 'query')

    assert np.allclose(graph.x.tolist(), [-0.5, -0.5, 1.0])
    assert np.allclose(graph.y.tolist(), [0.8660254037, -0.8660254037, 0.0])
    assert graph.url.tolist() == [4, 5, 1]
    assert graph.index.tolist() == [u'apple', u'banana', u'carrot']

def test_duplicate_multitag_rows(es_response):
    df = parse_es_response(es_response)

    # Refactored to be called inside of parse_es_response
    # df = duplicate_multi_rows(df, 'tag')

    assert df.shape == (10,5)
    assert df.tag.tolist() == ['Untagged', 'Untagged', u'Relevant', u'Relevant',
                               u'Irrelevant', u'Relevant', u'Irrelevant',
                               u'Relevant', u'Irrelevant', u'Relevant']

def test_normalize():
    assert np.allclose(normalize(pd.Series([1,2,3]), 3, 1.5).tolist(), [1.5, 2.0, 3.0])
