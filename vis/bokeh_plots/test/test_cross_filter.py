import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from ..cross_filter import parse_es_response

def test_parse_es_response():
    es_response = [
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:35.292'],
         u'tag': [u'Relevant'],
         u'url': [u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937']},
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:36.135'],
         u'tag': [u'Irrelevant', u'Relevant'],
         u'url': [u'http://www.applevacations.com/']},
        {u'query': [u'apple'],
         u'retrieved': [u'2016-04-16T00:06:34.806'],
         u'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU']}
    ]

    # note that data becomes ordered by `retrieved` field
    data = {'hostname': [u'reuters.com', u'politico.com', u'applevacations.com'],
            u'query': [u'apple', u'apple', u'apple'],
            u'tag': [[], [u'Relevant'], [u'Irrelevant', u'Relevant']],
             'tld': [u'.com', u'.com', u'.com'],
            u'url': [u'http://www.reuters.com/article/us-apple-encryption-hearing-idUSKCN0XB2RU',
                     u'http://www.politico.com/story/2016/04/apple-hires-cynthia-hogan-221937',
                     u'http://www.applevacations.com/']}

    df = parse_es_response(es_response)

    assert df.to_dict('list') == data
    assert df.index.dtype == np.dtype('datetime64[ns]')
