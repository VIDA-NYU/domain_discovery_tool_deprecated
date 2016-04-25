import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest

from ..cross_filter import (parse_es_response, calculate_query_correlation,
    calculate_graph_coords, munge_tags)

@pytest.fixture
def es_response():
    return [
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:35.292'],
         u'tag': [u'Relevant'],
         u'url': [u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937']},
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:36.135'],
         u'tag': [u'Irrelevant;Relevant'],
         u'url': [u'http://www.applevacations.com/']},
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:34.806'],
         u'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU']},
        {u'query': [u'banana'],
         u'retrieved': [u'2016-04-16T00:06:35.292'],
         u'tag': [u'Relevant'],
         u'url': [u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937']},
         {u'query': [u'banana'],
         u'retrieved': [u'2016-04-16T00:06:36.135'],
         u'tag': [u'Irrelevant;Relevant'],
         u'url': [u'http://www.applevacations.com/']},
         {u'query': [u'carrot'],
         u'retrieved': [u'2016-04-16T00:06:34.806'],
         u'url': [u'http://www.nytimes.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU']}
    ]


def test_parse_es_response(es_response):
    # note that data becomes ordered by `retrieved` field
    data = {'hostname': [u'reuters.com', u'nytimes.com', u'politico.com',
                         u'politico.com', u'applevacations.com', u'applevacations.com'],
            u'query': [u'apple', u'carrot', u'apple', u'banana', u'apple', u'banana'],
            u'tag': ["Untagged", "Untagged", u'Relevant', u'Relevant', u'Irrelevant;Relevant',
                     u'Irrelevant;Relevant'],
            'tld': [u'.com', u'.com', u'.com', u'.com', u'.com', u'.com'],
            u'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU',
                     u'http://www.nytimes.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU',
                     u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937',
                     u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937',
                     u'http://www.applevacations.com/',
                     u'http://www.applevacations.com/']}

    df = parse_es_response(es_response)

    assert df.to_dict('list') == data
    assert df.index.dtype == np.dtype('datetime64[ns]')

def test_calculate_query_correlation(es_response):
    df = parse_es_response(es_response)
    graph = calculate_query_correlation(df, 'query')

    assert graph == {(u'apple', u'banana'): 2, (u'apple', u'carrot'): 0, (u'carrot', u'banana'): 0}

def test_calculate_graph_coords(es_response):
    df = parse_es_response(es_response)
    graph = calculate_graph_coords(df, 'query')

    assert np.allclose(graph.x.tolist(), [0.0, 8.6031889e-08, 0.86602539])
    assert np.allclose(graph.y.tolist(), [1.0, 0.0, 0.5])
    assert graph.url.tolist() == [3, 2, 1]
    assert graph.index.tolist() == [u'apple', u'banana', u'carrot']

def test_munge_tags():
    data = ['Sports', 'Sports;Basketball', 'Sports;Baseball', 'Basketball', 'Sports;Basketball;NBA']
    counter = munge_tags(data)

    assert counter == {'Sports': 4, 'Basketball': 3, 'Baseball': 1, 'NBA': 1}
