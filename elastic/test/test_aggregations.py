from __future__ import absolute_import

import datetime
from mock import patch

from ..aggregations import get_unique_values, get_queries_pages

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

@patch('domain_discovery_tool.elastic.config.es.search')
def test_get_queries_pages(mock_es_search):
    mock_es_search.return_value = {
        u'_shards': {u'failed': 0,
                      u'successful': 5,
                      u'total': 5},
        u'aggregations': {u'queries': {u'buckets': [{u'doc_count': 3,
                                                     u'key': u'canavandl',
                                                     u'urls': {u'buckets': [{u'doc_count': 1,
                                                                             u'key': u'http://57f4dad48e7a4f7cd171c654226feb5a.extratorrent.filespook.com/questions/30896896/how-to-set-the-plot-object-name?rq=1'},
                                                                            {u'doc_count': 1,
                                                                             u'key': u'http://ebooksicilia.com/24842695-get-now-the-black-magician-trilogy-black-magician-1-3-by-trudi-canavan-download-pdf-mobi-epub-book.html'},
                                                                            {u'doc_count': 1,
                                                                             u'key': u'http://hn.premii.com/#/comments/11076390'}],
                                                     u'doc_count_error_upper_bound': 0,
                                                     u'sum_other_doc_count': 0}},
                                                    {u'doc_count': 3, u'key': u'canavandl.github.io',
                                                     u'urls': {u'buckets': [{u'doc_count': 1,
                                                     u'key': u'https://github.com/bokeh/bokeh/issues/2350'},
                                                    {u'doc_count': 1,
                                                     u'key': u'https://github.com/canavandl?tab=activity'},
                                                    {u'doc_count': 1,
                                                     u'key': u'https://github.com/canavandl?tab=repositories'}],
                                                     u'doc_count_error_upper_bound': 0,
                                                     u'sum_other_doc_count': 0}}],
                          u'doc_count_error_upper_bound': 0,
                          u'sum_other_doc_count': 0}},
        u'hits': {u'hits': [], u'max_score': 0.0, u'total': 22},
        u'timed_out': False,
        u'took': 3}

    result = {
        u'canavandl': [u'http://57f4dad48e7a4f7cd171c654226feb5a.extratorrent.filespook.com/questions/30896896/how-to-set-the-plot-object-name?rq=1',
                       u'http://ebooksicilia.com/24842695-get-now-the-black-magician-trilogy-black-magician-1-3-by-trudi-canavan-download-pdf-mobi-epub-book.html',
                       'http://hn.premii.com/#/comments/11076390'],
        u'canavandl.github.io': [u'https://github.com/bokeh/bokeh/issues/2350',
                                 u'https://github.com/canavandl?tab=activity',
                                 u'https://github.com/canavandl?tab=repositories']}

    assert get_queries_pages('query', 1000, es_index=u'canavandl.github.io', es_doc_type='page', es=None) == result
