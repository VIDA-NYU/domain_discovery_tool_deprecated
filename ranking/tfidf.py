import sys
import nltk
import math
import operator
import numpy as np
from os.path import exists

class tfidf:
    def __init__(self):
        self.documents = []
        self.corpus_dict = {}
        self.idf = {}
        self.tfidfVector = []
        self.exclude = []
        self.corpus_tf = {}
        if exists('exclude.txt'):
            with open('exclude.txt','r') as f:
                self.exclude = [word.strip() for word in f.readlines()];
            
    def getFreqDist(self, text):
        return nltk.probability.FreqDist(text)

    def getIdf(self):
        N = len(self.documents)
        for word in self.corpus_dict:
            self.idf[word] = math.log(float(N)/self.corpus_dict[word])

    def getTfidf(self):
        for [url, tf] in self.documents:
            doc_tfidf = {}
            for word in tf:
                doc_tfidf[word] = tf[word] * self.idf[word]
            self.tfidfVector.append([url,doc_tfidf])

    def getTopTerms(self,top):
        corpus = sorted(self.corpus_tf.items(), key=operator.itemgetter(1),reverse=True)
        return [x[0] for x in corpus[0:top]]

    def getIndex(self, terms):
        corpus = sorted(self.corpus_tf.items(), key=operator.itemgetter(1),reverse=True)
        corpus_keys = [x[0] for x in corpus]
        index = []
        for term in terms:
            index.append(corpus_keys.index(term.strip()))
        return index

    def getTfidfArray(self):
        corpus = sorted(self.corpus_tf.items(), key=operator.itemgetter(1),reverse=True)
        data = np.ndarray(shape=(len(self.tfidfVector),len(corpus)))
        index_i = 0
        for [url, vect] in self.tfidfVector:
            index_j = 0
            for [word, count] in corpus:
                data[index_i,index_j] = vect.get(word, 0.0)
                index_j = index_j + 1 
            index_i = index_i + 1
        return data

    def getTfArray(self):
        corpus = sorted(self.corpus_tf.items(), key=operator.itemgetter(1),reverse=True)
        data = np.ndarray(shape=(len(self.documents),len(corpus)))
        index_i = 0
        for [url, tf] in self.documents:
            index_j = 0
            for [word, count] in corpus:
                data[index_i,index_j] = tf.get(word, 0.0)
                index_j = index_j + 1 
            index_i = index_i + 1
        return data
    
    def getURLs(self, args):
        return [self.documents[x][0] for x in args]

    def getTerms(self, args):
        corpus = sorted(self.corpus_tf.items(), key=operator.itemgetter(1),reverse=True)
        return [corpus[x][0] for x in args]
        
    def process(self, inputfile, ignore_index):
        adjusted_indices = {}
        adjusted_index = 0
        with open(inputfile) as lines:
            count = 0
            for line in lines:
                if count not in ignore_index:
                    adjusted_indices[count] = adjusted_index
                    adjusted_index = adjusted_index + 1
                    url, content = line.split(";");
                    tokens = content.split(" ");
                    text = [ word.strip().strip('"') for word in nltk.Text(tokens) if word.strip().strip('"') not in self.exclude]
                
                    fdist = self.getFreqDist(text)

                    N = fdist.N()
                    for word in fdist:
                        self.corpus_dict[word] = self.corpus_dict.get(word,0.0) + 1.0
                        self.corpus_tf[word] = self.corpus_tf.get(word,0.0) + fdist[word]
                        fdist[word] = fdist[word] / float(N)
                    self.documents.append([url,fdist])
                count = count + 1
        self.getIdf()
        self.getTfidf()
        return adjusted_indices
            
                    


