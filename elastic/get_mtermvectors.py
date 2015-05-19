#!/usr/bin/env python
from sklearn.feature_extraction import DictVectorizer
import nltk
import sys
import pprint
import math
from os import environ
from elasticsearch import Elasticsearch

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

def tfidf(tf, df, n_doc):
    idf = math.log(n_doc / float(df))
    return tf * idf

def terms_from_es_json(doc, rm_stopwords=True, pos_tags=[]):
    terms = {}
    docterms = doc["term_vectors"]["text"]["terms"]
    n_doc = doc["term_vectors"]["text"]["field_statistics"]["doc_count"]
    valid_words = docterms.keys()
    if rm_stopwords:
        no_stopwords = [k for k in docterms.keys() if k not in ENGLISH_STOPWORDS and (len(k) > 2)]
        valid_words = no_stopwords

    if len(pos_tags) > 0:
        tagged = nltk.pos_tag(docterms)
        #tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VBN', 'JJ']
        valid_words = [tag[0] for tag in tagged if tag[1] in tags]

    for k in valid_words:
        try:
            terms[k] = tfidf(docterms[k]["term_freq"], docterms[k]["doc_freq"], n_doc)
        except KeyError:
            print k, " ", docterms[k]

    return terms

def getTermStatistics(all_hits):
    host =  environ['ELASTICSEARCH_SERVER'] if environ.get('ELASTICSEARCH_SERVER') else 'localhost'
    es = Elasticsearch(hosts=[host])
    tfidfs = []
    docs = []

    for i in range(0, len(all_hits), 100):
        hits = all_hits[i:i+100]
        term_res = es.mtermvectors(index=environ['ELASTICSEARCH_INDEX'] if environ.get('ELASTICSEARCH_INDEX') else 'memex', 
                                doc_type=environ['ELASTICSEARCH_DOC_TYPE'] if environ.get('ELASTICSEARCH_DOC_TYPE') else 'page', 
                                term_statistics=True, fields=['text'], ids=hits)
        #pprint.pprint(term_res['docs'])
        for doc in term_res['docs']:
            #pprint.pprint(doc)
            if doc.get('term_vectors'):
                if 'text' in doc['term_vectors']:
                    docs.append(doc['_id'])
                    tfidfs.append(terms_from_es_json(doc))
            #else:
             #   pprint.pprint(doc)
        #pprint.pprint(tfidfs)
    
    v = DictVectorizer()

    return [v.fit_transform(tfidfs), v.get_feature_names()]

