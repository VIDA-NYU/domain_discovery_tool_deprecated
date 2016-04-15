from __future__ import absolute_import

import datetime
from mock import patch

from ..get_config import get_available_domains, get_tag_colors, convert_to_epoch

@patch('domain_discovery_tool.elastic.config.es.search')
def test_get_available_domains(mock_es_search):
    mock_es_search.return_value = {
        u'_shards': {u'failed': 0, u'successful': 5, u'total': 5},
        u'hits': {u'hits': [{u'_id': u'AVMvFWO9MkmXpgbxTSHg',
                             u'_index': u'config',
                             u'_score': 1.0,
                             u'_source': {u'doc_type': u'page',
                                          u'domain_name': u'Potatoes',
                                          u'index': u'potatoes',
                                          u'timestamp': u'2016-02-29T22:10:44.280923'},
                             u'_type': u'domains'},
                            {u'_id': u'AVQbqH4KaDi0obA2Guq2',
                             u'_index': u'config',
                             u'_score': 1.0,
                             u'_source': {u'doc_type': u'page',
                                          u'domain_name': u'Apple',
                                          u'index': u'apple',
                                          u'timestamp': u'2016-04-15T20:41:47.776854'},
                             u'_type': u'domains'}],
                  u'max_score': 1.0,
                  u'total': 2},
                  u'timed_out': False,
                  u'took': 1
     }

    result = {'AVMvFWO9MkmXpgbxTSHg': {'doc_type': 'page',
                                       'domain_name': 'Potatoes',
                                       'index': 'potatoes',
                                       'timestamp': 1456783844L},
              'AVQbqH4KaDi0obA2Guq2': {'doc_type': 'page',
                                       'domain_name': 'Apple',
                                       'index': 'apple',
                                       'timestamp': 1460752907L}}

    assert get_available_domains() == result

@patch('domain_discovery_tool.elastic.config.es.search')
def test_get_tag_colors(mock_es_search):
    mock_es_search.return_value = {
        u'_shards': {u'failed': 0, u'successful': 5, u'total': 5},
                     u'hits': {u'hits': [{u'_id': u'AVMvFWO9MkmXpgbxTSHg',
                                          u'_index': u'config',
                                          u'_score': 1.0,
                                          u'_source': {u'colors': [u'SuperCool;Coral',
                                                                   u'Neat;GoldenRod'],
                                                       u'index': 2},
                                          u'_type': u'tag_colors'}],
                               u'max_score': 1.0,
                               u'total': 1},
                     u'timed_out': False,
                     u'took': 1
        }

    result = {u'AVMvFWO9MkmXpgbxTSHg': {'colors': [u'SuperCool;Coral',
                                                   u'Neat;GoldenRod'],
                                        'index': 2}}

    assert get_tag_colors() == result

def test_convert_to_epoch():
    assert convert_to_epoch(datetime.datetime(1970,01,01)) == 0
    assert convert_to_epoch(datetime.datetime(2000,01,01)) == 946684800
