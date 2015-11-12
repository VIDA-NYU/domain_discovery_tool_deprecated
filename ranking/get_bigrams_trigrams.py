from elasticsearch import Elasticsearch
from elastic.get_documents import get_documents
from sklearn.feature_extraction.text import CountVectorizer
import operator

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

def get_bigrams_trigrams(text=[], termCount=20, w2v=None, es=None):
        
        bigram_vectorizer = CountVectorizer(ngram_range=(2,2))
        bigram_analyze = bigram_vectorizer.build_analyzer()
        trigram_vectorizer = CountVectorizer(ngram_range=(3,3))
        trigram_analyze = trigram_vectorizer.build_analyzer()
        
        bi_results= map(lambda t: bigram_analyze(t), text)
        tri_results= map(lambda t: trigram_analyze(t), text)
        
        bigrams = []
        bi_dict_corpus = {}
        for doc in bi_results:
                bi_dict={}
                for bi in doc:
                        bi=bi.replace(' ','_')
                        if bi in bi_dict:
                                bi_dict[bi] = bi_dict[bi] + 1
                        else:
                                bi_dict[bi] = 1 
                                
                if bi_dict:
                        # Yamuna: Removing for now as it is slow
                        #phrases = remove_stopword_phrases(bi_dict.keys())        
                        phrases = bi_dict.keys()
                        if w2v.word_vec is None:
                                results = get_documents(phrases, "term", ["term"], "word_phrase_to_vec", "terms", es)
                                phrases = [res.lower() for res in results.keys()]
                        else:
                                phrases = [term for term in phrases if not w2v.get(term) is None]
                        
        
                        bi_dict_subset = {phrase: bi_dict[phrase] for phrase in phrases}
                        if bi_dict_subset:
                                bigrams.append(bi_dict_subset)
                                for phrase in bi_dict_subset.keys():
                                        if phrase in bi_dict_corpus:
                                                bi_dict_corpus[phrase] = bi_dict_corpus[phrase] + bi_dict_subset[phrase]
                                        else:
                                                bi_dict_corpus[phrase] = bi_dict_subset[phrase]
                                                
                        
        trigrams = []
        tri_dict_corpus = {}
        for doc in tri_results:
                tri_dict={}
                for tri in doc:
                        tri=tri.replace(' ','_')
                        if tri in tri_dict:
                                tri_dict[tri] = tri_dict[tri] + 1
                        else:
                                tri_dict[tri] = 1
                if tri_dict:
                        # Yamuna: Removing for now as it is slow
                        #phrases = remove_stopword_phrases(tri_dict.keys())        
                        phrases = tri_dict.keys()
                        if w2v.word_vec is None:
                                results = get_documents(phrases, "term", ["term"], "word_phrase_to_vec", "terms", es)
                                phrases = [res for res in results.keys()]
                        else:
                                phrases = [term for term in phrases if not w2v.get(term) is None]

                        tri_dict_subset = {phrase: tri_dict[phrase] for phrase in phrases}
                        if tri_dict_subset:
                                trigrams.append(tri_dict_subset)
                                for phrase in tri_dict_subset.keys():
                                        if phrase in tri_dict_corpus:
                                                tri_dict_corpus[phrase] = tri_dict_corpus[phrase] + tri_dict_subset[phrase]
                                        else:
                                                tri_dict_corpus[phrase] = tri_dict_subset[phrase]
                                                
        return bigrams, trigrams, sorted(bi_dict_corpus.items(), key=operator.itemgetter(1), reverse=True)[0:termCount], sorted(tri_dict_corpus.items(), key=operator.itemgetter(1), reverse=True)[0:termCount]

