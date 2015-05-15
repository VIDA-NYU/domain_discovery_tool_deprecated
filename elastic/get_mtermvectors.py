#!/usr/bin/env python
from sklearn.feature_extraction import DictVectorizer
import sys
import pprint
import math
import os

from elasticsearch import Elasticsearch
from generators import *

def get_tfidfs():
    es_server = 'http://localhost:9200/'
    if os.environ.get('ELASTICSEARCH_SERVER'):
        es_server = os.environ['ELASTICSEARCH_SERVER']
    es = Elasticsearch(es_server)
    
    ids = ids_generator(es, index='memex', doc_type='page')
    tfidfs = []
    docs = []
    for (id, term_vector) in termvectors_generator(es, index='memex', doc_type='page', ids_generator=ids, fields=['text'], size=10):
        tfidfs.append(term_vector)
        docs.append(id)

    v = DictVectorizer()
    X_tfidf = v.fit_transform(tfidfs)
    Vocab = v.get_feature_names()
    return [X_tfidf, Vocab]

if __name__ == "__main__":
    print get_tfidfs()

