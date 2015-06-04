import sys
import nltk
import math
import operator
import numpy as np
from os.path import exists
from collections import OrderedDict
from elastic.get_mtermvectors import getTermStatistics

class tfidf:
    def __init__(self, opt_docs = None, es_index = 'memex', es_doc_type = 'page', es = None):
        self.documents = opt_docs
        self.corpus = None
        self.tfidfArray = None
        self.tfArray = None
        self.ttf = None
        if opt_docs != None:
          self.process(opt_docs, es_index, es_doc_type, es)

    def getTopTerms(self,top):
        N = len(self.documents)
        avg = np.divide(np.sum(self.tfidfArray.toarray(), axis=0), N)
        sortedAvgIndices = np.argsort(avg)[::-1]
        return [self.corpus[i] for i in sortedAvgIndices[0:top]]

    def getIndex(self, terms):

        index = []
        for term in terms:
            if term.strip() in self.corpus:
                index.append(self.corpus.index(term.strip()))
        return index

    def getTfidfArray(self):
        return [self.documents, self.corpus, self.tfidfArray]

    def getTfArray(self):
        return [self.documents, self.corpus, self.tfArray]

    def getTtf(self):
        return self.ttf

    def getURLs(self, args):
        return self.documents

    def getTerms(self, indices):
        return [self.corpus[x] for x in indices]

    def process(self, documents, es_index = 'memex', es_doc_type = 'page', es = None):
        [data_tfidf, data_tf, data_ttf, corpus] = getTermStatistics(documents, es_index, es_doc_type, es)
        self.tfidfArray = data_tfidf
        self.tfArray = data_tf
        self.ttf = data_ttf
        self.corpus = corpus
