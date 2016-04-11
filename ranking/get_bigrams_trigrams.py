from elasticsearch import Elasticsearch
from elastic.get_documents import get_documents
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
import numpy as np
import operator
import math

from nltk import corpus
ENGLISH_STOPWORDS = set(corpus.stopwords.words('english'))

from pprint import pprint

def remove_stopword_phrases(phrases):
        selected_phrases = []
        for phrase in phrases:
                words = phrase.split('_');
                if not words[0] in ENGLISH_STOPWORDS:
                        selected_phrases.append(phrase)
        return selected_phrases

def get_bigrams_trigrams(text=[], urls=[], termCount=20, w2v=None, es=None):
        
        bigram_vectorizer = CountVectorizer(ngram_range=(2,2))
        bigram_analyze = bigram_vectorizer.build_analyzer()
        trigram_vectorizer = CountVectorizer(ngram_range=(3,3))
        trigram_analyze = trigram_vectorizer.build_analyzer()
        
        bi_results= map(lambda t: bigram_analyze(t), text)
        tri_results= map(lambda t: trigram_analyze(t), text)

        index = 0
        bigrams = []
        bi_dict_corpus = {}
        bi_dict_df = {}
        for doc in bi_results:
                bi_dict={}
                for bi in doc:
                        if bi in bi_dict:
                                bi_dict[bi] = bi_dict[bi] + 1
                        else:
                                bi_dict[bi] = 1

                bigrams.append(bi_dict)
                
                for phrase in bi_dict.keys():
                        if phrase in bi_dict_corpus:
                                bi_dict_corpus[phrase] = bi_dict_corpus[phrase] + bi_dict[phrase]
                        else:
                                bi_dict_corpus[phrase] = bi_dict[phrase]

                        if phrase in bi_dict_df:
                                bi_dict_df[phrase] = bi_dict_df[phrase] + 1
                        else:
                                bi_dict_df[phrase] = 1
        
        bigrams_tfidf = []
        for bigram in bigrams:
                bigrams_dict_tfidf = {}
                for phrase in bigram.keys():
                        if bi_dict_df[phrase] > 0: #(len(bigrams)/3):
                                bigrams_dict_tfidf[phrase] = bigram[phrase] * (math.log(len(bigrams)/ float(1+bi_dict_df[phrase])))
                bigrams_tfidf.append(bigrams_dict_tfidf)
                                                
        trigrams = []
        tri_dict_corpus = {}
        tri_dict_df = {}
        
        for doc in tri_results:

                tri_dict={}
                for tri in doc:
                        if tri in tri_dict:
                                tri_dict[tri] = tri_dict[tri] + 1
                        else:
                                tri_dict[tri] = 1
                trigrams.append(tri_dict)
        
                for phrase in tri_dict.keys():
                        if phrase in tri_dict_corpus:
                                tri_dict_corpus[phrase] = tri_dict_corpus[phrase] + tri_dict[phrase]
                        else:
                                tri_dict_corpus[phrase] = tri_dict[phrase]

                        if phrase in tri_dict_df:
                                tri_dict_df[phrase] = tri_dict_df[phrase] + 1
                        else:
                                tri_dict_df[phrase] = 1
        trigrams_tfidf = []
        for trigram in trigrams:
                trigrams_dict_tfidf = {}
                for phrase in trigram.keys():
                        if tri_dict_df[phrase] > 0: #(len(trigrams)/3):
                                trigrams_dict_tfidf[phrase] = trigram[phrase] * (math.log(len(trigrams)/ float(1+tri_dict_df[phrase])))
                trigrams_tfidf.append(trigrams_dict_tfidf)
                
        v_bigram_tfidf = DictVectorizer()
        bigram_tfidf_data = v_bigram_tfidf.fit_transform(bigrams_tfidf).toarray()
        bigram_corpus = v_bigram_tfidf.get_feature_names()
        v_bigram_tf = DictVectorizer()
        bigram_tf_data = v_bigram_tf.fit_transform(bigrams).toarray()
                
        N = len(bigrams)
        avg = np.divide(np.sum(bigram_tfidf_data, axis=0), N)
        sortedAvgIndices = np.argsort(avg)[::-1]
        top_bigrams = [bigram_corpus[i] for i in sortedAvgIndices[0:termCount]]

        v_trigram_tfidf = DictVectorizer()
        trigram_tfidf_data = v_trigram_tfidf.fit_transform(trigrams_tfidf).toarray()
        trigram_corpus = v_trigram_tfidf.get_feature_names()
        v_trigram_tf = DictVectorizer()
        trigram_tf_data = v_trigram_tf.fit_transform(trigrams).toarray()
        
        N = len(trigrams)
        avg = np.divide(np.sum(trigram_tfidf_data, axis=0), N)
        sortedAvgIndices = np.argsort(avg)[::-1]
        top_trigrams = [trigram_corpus[i] for i in sortedAvgIndices[0:termCount]]

        return bigram_tfidf_data, trigram_tfidf_data, bigram_tf_data, trigram_tf_data, bigram_corpus, trigram_corpus, bi_dict_corpus, tri_dict_corpus, top_bigrams, top_trigrams
