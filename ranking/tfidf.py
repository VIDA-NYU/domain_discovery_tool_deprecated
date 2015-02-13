import sys
import nltk
import math
import operator
import numpy as np

class tfidf:
    def __init__(self):
        self.documents = []
        self.corpus_dict = {}
        self.idf = {}
        self.tfidfVector = []

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

    def getTfidfArray(self):
        corpus = sorted(self.corpus_dict.items(), key=operator.itemgetter(0))
        data = np.ndarray(shape=(len(self.tfidfVector),len(corpus)))
        index_i = 0
        for [url, vect] in self.tfidfVector:
            index_j = 0
            for [word, count] in corpus:
                data[index_i,index_j] = vect.get(word, 0.0)
                index_j = index_j + 1 
            index_i = index_i + 1
        return data
    
    def getURLs(self, args):
        return [self.documents[x][0] for x in args]
        
    def process(self, inputfile):
        with open(inputfile) as lines:
            for line in lines:
                url, content = line.split(";");
                tokens = content.split(" ");
                text = nltk.Text(tokens)
                fdist = self.getFreqDist(text)

                N = fdist.N()
                for word in fdist:
                    fdist[word] = fdist[word] / float(N)
                    self.corpus_dict[word] = self.corpus_dict.get(word,0.0) + 1.0

                self.documents.append([url,fdist])
            self.getIdf()
            self.getTfidf()
            
                    


