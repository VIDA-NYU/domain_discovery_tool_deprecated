import sys
import nltk
import math
import operator
import numpy as np
from os.path import exists
from collections import OrderedDict
from elastic.get_mtermvectors import getTermStatistics

class tfidf:
    def __init__(self, opt_docs = None):
        self.documents = opt_docs
        self.corpus = None
        self.tfidfArray = None
        if opt_docs != None:
          self.process(opt_docs)

    def getTopTerms(self,top):
        N = len(self.documents)
        avg = np.divide(np.sum(self.tfidfArray.toarray(), axis=0), N)
        sortedAvgIndices = np.argsort(avg)[::-1]
        return [self.corpus[i] for i in sortedAvgIndices[0:top]]

    def getIndex(self, terms):
        print "TERMS = ", terms
        index = []
        for term in terms:
            if term.strip() in self.corpus:
                index.append(self.corpus.index(term.strip()))
        print "INDICES = ", index
        return index

    def getTfidfArray(self):
        return [self.documents, self.corpus, self.tfidfArray.toarray()]

    def getURLs(self, args):
        return self.documents

    def getTerms(self, indices):
        return [self.corpus[x] for x in indices]

    def process(self, documents):
        [data, corpus] = getTermStatistics(documents)
        self.tfidfArray = data
        self.corpus = corpus
