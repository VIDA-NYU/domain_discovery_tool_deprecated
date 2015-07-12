#!/usr/bin/env python
from sklearn.feature_extraction import DictVectorizer
import nltk
import math
from sets import Set
import time

from config import es_elastic as default_es

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))

def tfidf(tf, df, n_doc):
    idf = math.log(n_doc / float(df))
    return tf * idf

def terms_from_es_json(doc, w2v=None, rm_stopwords=True, pos_tags=[], termstatistics = False):
    terms = {}
    docterms = doc["term_vectors"]["text"]["terms"]
    n_doc = doc["term_vectors"]["text"]["field_statistics"]["doc_count"]
    valid_words = docterms.keys()
    
    if rm_stopwords:
        no_stopwords = [k for k in docterms.keys() if k not in ENGLISH_STOPWORDS and (len(k) > 2)]
        valid_words = no_stopwords

    if not w2v is None:
        valid_words = [term for term in valid_words if not w2v.get(term) is None]

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


def getTermFrequency(all_hits, w2v=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    docs = []
    stats = []
    corpus = []

    count = 0
    time_sum_for_method = 0
    time_sum_for_process = 0

    for i in range(0, len(all_hits), 10):
        count = count + 1
        hits = all_hits[i:i+10]

        start = time.clock()
        term_res = es.mtermvectors(index=es_index,
                                   doc_type=es_doc_type,
                                   fields=['text'], 
                                   ids=hits) 
        
        time_sum_for_method = time_sum_for_method + (time.clock() - start)

        start = time.clock()
        for doc in term_res['docs']:
            if doc.get('term_vectors'):
                if 'text' in doc['term_vectors']:
                    docs.append(doc['_id'])
                    res = terms_from_es_json(doc=doc, w2v=w2v)
                    stats.append(res)
                    corpus = corpus + res.keys()
        time_sum_for_process = time_sum_for_process + (time.clock() - start)

    return [stats, Set(corpus), docs]

def getTermStatistics(all_hits, w2v=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    stats = []
    docs = []

    count = 0
    time_sum_for_method = 0
    time_sum_for_process = 0

    ttf = {}
    for i in range(0, len(all_hits), 10):
        count = count + 1
        hits = all_hits[i:i+10]

        start = time.clock()
        term_res = es.mtermvectors(index=es_index,
                                   doc_type=es_doc_type,
                                   term_statistics=True, 
                                   fields=['text'], 
                                   ids=hits)
        time_sum_for_method = time_sum_for_method + (time.clock() - start)

        start = time.clock()
        for doc in term_res['docs']:
            if doc.get('term_vectors'):
                if 'text' in doc['term_vectors']:
                    docs.append(doc['_id'])
                    res = terms_from_es_json(doc=doc, w2v=w2v, termstatistics=True)
                    stats.append(res)
                    for k in res.keys():
                        ttf[k] = res[k]['ttf']
        time_sum_for_process = time_sum_for_process + (time.clock() - start)
    
    start = time.clock()
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

    time_sum_for_process = time_sum_for_process + (time.clock() - start)

    return result

