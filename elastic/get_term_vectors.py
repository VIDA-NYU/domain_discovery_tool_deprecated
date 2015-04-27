#!/usr/bin/python
from elasticsearch import ElasticSearch
import sys
from os import environ

es_server = 'http://localhost:9200/'
if environ.get('ELASTICSEARCH_SERVER'):
    es_server = environ['ELASTICSEARCH_SERVER']
es = ElasticSearch(es_server)

query = {
    "query": {
        "match_all": {}
    },
    "fields": []
}
res = es.search(query, index='memex', doc_type='page')
hits = res['hits']
print 'Document found: %d' % hits['total']
ids = [hit['_id'] for hit in hits['hits']]
body={
    "ids": ids,
    "parameters": {
        "fields": [ "text" ]
    }
}
res = es.send_request('POST',
                      ['memex', 'page', '_mtermvectors'],
                      body=body, query_params={})

