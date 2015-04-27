#!/usr/bin/python
from elasticsearch import Elasticsearch
from sklearn.feature_extraction import DictVectorizer
import sys
import pprint
from os import environ
import math

es_server = 'http://localhost:9200/'
if environ.get('ELASTICSEARCH_SERVER'):
    es_server = environ['ELASTICSEARCH_SERVER']
es = Elasticsearch(es_server)

query = {
    "query": {
        "match_all": {}
    }
}

def tfidf(tf, df, n_docs):
    idf = math.log(n_docs / float(df))
    return tf * idf

def terms_from_es_json(doc):
    terms = {}
    docterms = doc["term_vectors"]["text"]["terms"]
    n_doc = doc["term_vectors"]["text"]["field_statistics"]["doc_count"]
    for k, v in docterms.iteritems():
        terms[k] = tfidf(v["term_freq"], v["doc_freq"], n_doc)
    return terms

res = es.search(body=query, index='memex', doc_type='page',fields=[],scroll='1m',search_type='scan', size=100)
all_hits = res['hits']['hits']
tfidfs = []
docs = []

#pprint.pprint(res)
print 'Document found: %d' % res['hits']['total']
while '_scroll_id' in res:
    res = es.scroll(scroll_id=res['_scroll_id'])
#    pprint.pprint(res)
    hits = [hit['_id'] for hit in res['hits']['hits']]
    all_hits += hits


for i in range(0, len(all_hits), 100):
    hits = all_hits[i:i+100]
    term_res = es.mtermvectors(index='memex', doc_type='page', term_statistics=True, fields=['text'], ids=hits)
    #    pprint.pprint(term_res['docs'])
    for doc in term_res['docs']:
        #pprint.pprint(doc)
        if 'text' in doc["term_vectors"]:
            docs.append(doc['_id'])
            tfidfs.append(terms_from_es_json(doc))

#pprint.pprint(tfidfs)

v = DictVectorizer()
X_tfidf = v.fit_transform(tfidfs)

pprint.pprint(X_tfidf)
