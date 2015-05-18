#!/usr/bin/python
from elasticsearch import Elasticsearch
from sklearn.feature_extraction import DictVectorizer
import nltk
import sys
import pprint
from os import environ
import math
from get_all_documents import get_all_documents

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

def tfidf(tf, df, n_docs):
    idf = math.log(n_docs / float(df))
    return tf * idf

def terms_from_es_json(doc):
    terms = {}
    docterms = doc["term_vectors"]["text"]["terms"]
    n_doc = doc["term_vectors"]["text"]["field_statistics"]["doc_count"]
    no_stopwords = [k for k in docterms.keys() if k not in ENGLISH_STOPWORDS and (len(k) > 2)]
    #print no_stopwords, "\n"
    tagged = nltk.pos_tag(no_stopwords)
    #print tagged, "\n"
    tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VBN', 'JJ']
    valid_words = [tag[0] for tag in tagged if tag[1] in tags]
    #print valid_words, "\n"
    for k in valid_words:
        terms[k] = tfidf(docterms[k]["term_freq"], docterms[k]["doc_freq"], n_doc)
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

if __name__ == "__main__":
    
    res = get_all_documents(fields = ["url"])
    #pprint.pprint(res)
    
    all_hits = [hit['_id'] for hit in res]
    #pprint.pprint(all_hits)
    [_, features] = getTermStatistics(all_hits)
    print features
