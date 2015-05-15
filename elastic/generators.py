#!/usr/bin/env python

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import math

__export__ = ['ids_generator', 'termvectors_generator' ]

def ids_generator(es, index, doc_type):
    for res in scan(es, index=index, doc_type=doc_type, query={ "query": { "match_all": {} } }, fields=[]):
        yield res['_id']


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

def termvectors_generator(es, index, doc_type, ids_generator, fields=None, size=100):
    ids = []
    for id in ids_generator:
        ids.append(id)
        if (len(ids)>=size):
            term_res = es.mtermvectors(index=index, doc_type=doc_type, term_statistics=True, fields=fields, ids=ids)
            for doc in term_res['docs']:
                if 'term_vectors' in doc and fields[0] in doc["term_vectors"]:
                    yield (doc['_id'], terms_from_es_json(doc))
            ids = []

if __name__ == "__main__":
    all_hits = []
    #for hits in search_generator(es, index='memex', doc_type='page'):
    for id in ids_generator(es, index='memex', doc_type='page'):
        all_hits.append(id)

    print 'Found %d hits'% len(all_hits)

    terms = []
    docs = []
    ids_gen = ids_generator(es, index='memex', doc_type='page')
    for (id, term_vector) in termvectors_generator(es, index='memex', doc_type='page', ids_generator=all_hits, fields=['text'], size=10):
        terms.append(term_vector)
        docs.append(id)
    
    print len(terms)
