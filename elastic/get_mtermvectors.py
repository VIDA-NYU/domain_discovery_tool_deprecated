#!/usr/bin/env python
from sklearn.feature_extraction import DictVectorizer
import nltk
import math
from sets import Set
import time

from config import es as default_es
from elastic.get_documents import get_documents_by_id

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

def tfidf(tf, df, n_doc):
    idf = math.log(n_doc / float(df))
    return tf * idf

def terms_from_es_json(doc, rm_stopwords=True, pos_tags=[], termstatistics = False, mapping=None, es=None):
    terms = {}
    docterms = doc["term_vectors"][mapping['text']]["terms"]
    n_doc = doc["term_vectors"][mapping['text']]["field_statistics"]["doc_count"]
    valid_words = docterms.keys()
    
    if rm_stopwords:
        no_stopwords = [k for k in docterms.keys() if k not in ENGLISH_STOPWORDS and (len(k) > 2)]
        valid_words = no_stopwords

    if len(pos_tags) > 0:
        tagged = nltk.pos_tag(docterms)
        #tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VBN', 'JJ']
        valid_words = [tag[0] for tag in tagged if tag[1] in tags]
        
    if termstatistics == True:
        terms = {term: {'tfidf':tfidf(docterms[term]["term_freq"], docterms[term]["doc_freq"], n_doc),
                        'tf': docterms[term]["term_freq"],
                        'ttf': docterms[term]["ttf"],
                    } for term in valid_words if docterms[term]["ttf"] > 1
        }
    else:
        terms = { term: {'tf': docterms[term]} for term in valid_words }

    return terms


def getTermFrequency(all_hits, mapping=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    docs = []
    stats = []
    corpus = []

    once = True
    for i in range(0, len(all_hits), 10):
        hits = all_hits[i:i+10]

        term_res = es.mtermvectors(index=es_index,
                                   doc_type=es_doc_type,
                                   fields=mapping['text'], 
                                   ids=hits) 

        for doc in term_res['docs']:
            if doc.get('term_vectors'):
                if mapping['text'] in doc['term_vectors']:
                    docs.append(doc['_id'])
                    res = terms_from_es_json(doc=doc, mapping=mapping)
                    stats.append(res)
                    corpus = corpus + res.keys()

    return [stats, Set(corpus), docs]

def getTermStatistics(all_hits, mapping=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    stats = []
    docs = []

    ttf = {}
    for i in range(0, len(all_hits), 10):
        hits = all_hits[i:i+10]

        term_res = es.mtermvectors(index=es_index,
                                   doc_type=es_doc_type,
                                   term_statistics=True, 
                                   fields=mapping['text'], 
                                   ids=hits)

        for doc in term_res['docs']:
            if doc.get('term_vectors'):
                if mapping['text'] in doc['term_vectors']:
                    docs.append(doc['_id'])
                    res = terms_from_es_json(doc=doc, termstatistics=True, mapping=mapping)
                    stats.append(res)
                    for k in res.keys():
                        ttf[k] = res[k]['ttf']

    tfidfs = []
    for stat in stats:
        tfidf={}
        for k in stat.keys():
            tfidf[k] =stat[k]['tfidf']
        tfidfs.append(tfidf)

    tfs = []
    for stat in stats:
        tf={}
        for k in stat.keys():
            tf[k] =stat[k]['tf']
        tfs.append(tf)
    
    v_tfidf = DictVectorizer()
    v_tf = DictVectorizer()

    result = [v_tfidf.fit_transform(tfidfs), v_tf.fit_transform(tfs), ttf, v_tfidf.get_feature_names(), docs]

    return result

