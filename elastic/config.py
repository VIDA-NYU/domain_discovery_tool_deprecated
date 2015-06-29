'''
provides access to elasticsearch server

es_server - the name of the endpoint
es - an Elasticsearch instance connected to es_server
'''

from pyelasticsearch import ElasticSearch
from os import environ


if environ.get('ELASTICSEARCH_SERVER'):
    es_server = environ['ELASTICSEARCH_SERVER']
else:
    es_server = 'http://localhost:9200/'

print "ElasticSearch endpoint: %s" % es_server
es = ElasticSearch(es_server)

