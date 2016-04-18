from __future__ import absolute_import

import datetime
from mock import patch

from ..aggregations import get_unique_values

@patch('domain_discovery_tool.elastic.config.es.search')
def test_get_unique_values(mock_es_search):
    mock_es_search.return_value = {
        u'hits': {u'hits': [],
                  u'total': 549,
                  u'max_score': 0.0},
        u'_shards': {u'successful': 5,
                     u'failed': 0,
                     u'total': 5},
        u'took': 4,
        u'aggregations': {u'unique_values': {u'buckets': [{u'key': u'Relevant', u'doc_count': 72},
                                                          {u'key': u'Neat;Relevant', u'doc_count': 27},
                                                          {u'key': u'Irrelevant', u'doc_count': 19},
                                                          {u'key': u'Neat', u'doc_count': 17},
                                                          {u'key': u'Neat;Irrelevant', u'doc_count': 13},
                                                          {u'key': u'Irrelevant;SuperCool', u'doc_count': 12},
                                                          {u'key': u'Cool stuff', u'doc_count': 8},
                                                          {u'key': u'', u'doc_count': 4},
                                                          {u'key': u'Relevant;Neat', u'doc_count': 1}],
                                             u'sum_other_doc_count': 0,
                                             u'doc_count_error_upper_bound': 0}},
        u'timed_out': False}

    result = {u'': 4,
              u'Cool stuff': 8,
              u'Irrelevant': 19,
              u'Irrelevant;SuperCool': 12,
              u'Neat': 17,
              u'Neat;Irrelevant': 13,
              u'Neat;Relevant': 27,
              u'Relevant': 72,
              u'Relevant;Neat': 1}

    assert get_unique_values('tag', 10000, es_index=u'potatoes', es_doc_type='page', es=None) == result
