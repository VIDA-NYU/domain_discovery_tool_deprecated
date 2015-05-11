from elasticsearch import Elasticsearch
from os import environ

__export__ = ['es_server', 'es']

es_server = 'http://localhost:9200/'
if environ.get('ELASTICSEARCH_SERVER'):
    es_server = environ['ELASTICSEARCH_SERVER']
es = Elasticsearch(es_server)


