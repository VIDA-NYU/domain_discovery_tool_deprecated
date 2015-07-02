from pickle import load
import numpy as np
from os import environ
from pprint import pprint

from elastic.get_mtermvectors import getTermStatistics

class word2vec:
    def __init__(self, opt_docs = None, es_index = 'memex', es_doc_type = 'page', es = None):
        self.documents = opt_docs
        self.word2vec = None

        if opt_docs != None:
            self.process(opt_docs, es_index, es_doc_type, es)

    def get_word2vec(self):
        return [self.documents,self.word2vec]
        
    def process(self, documents, es_index = 'memex', es_doc_type = 'page', es = None):

        [data_tfidf, data_tf, data_ttf, corpus, urls] = getTermStatistics(documents, es_index, es_doc_type, es)
        
        f = open(environ['DDT_HOME']+'/ranking/D_cbow_pdw_8B.pkl', 'rb')
        word_vec = load(f)
        
        word2vec_list_docs = []
        data_tf_array = data_tf.toarray()
        urls = []
        for i in range(0,np.shape(data_tf_array)[0]):
            word_tf_doc = data_tf_array[i]
            word_vec_doc = [word_vec[corpus[j]] for j in range(0,len(word_tf_doc)) if word_tf_doc[j] > 5 and not word_vec.get(corpus[j]) is None]
            if word_vec_doc:
                m_word_vec = np.array(word_vec_doc).mean(axis=0) 
                word2vec_list_docs.append(m_word_vec.tolist())
                urls.append(self.documents[i])
        
        self.documents = urls
        
        self.word2vec = np.array(word2vec_list_docs)
        
        
