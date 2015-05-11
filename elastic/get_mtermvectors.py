#!/usr/bin/env python
from sklearn.feature_extraction import DictVectorizer
import sys
import pprint
import math

from elastic import *
from .generators import *

def get_tfidfs():
    ids = ids_generator(es, index='memex', doc_type='page')
    tfidfs = []
    docs = []
    for (id, term_vector) in termvectors_generator(es, index='memex', doc_type='page', ids_generator=ids, fields=['text'], size=10):
        tfids.append(term_vector)
        docs.append(id)

    v = DictVectorizer()
    X_tfidf = v.fit_transform(tfidfs)
    return X_tfidf

