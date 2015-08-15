from elasticsearch import Elasticsearch
from elastic.get_documents import get_documents_by_id
from sklearn.feature_extraction.text import CountVectorizer
import operator

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
                        if w2v.word_vec is None:
                                results = get_documents_by_id(bi_dict.keys(), ["term"], "word_phrase_to_vec", "terms", es)
                                phrases = [res["term"][0] for res in results]
                        else:
                                phrases = [term for term in bi_dict.keys() if not w2v.get(term) is None]
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
                        if w2v.word_vec is None:
                                phrases = tri_dict.keys()
                                results = get_documents_by_id(phrases, ["term"], "word_phrase_to_vec", "terms", es)
                                phrases = [res["term"][0] for res in results]
                        else:
                                phrases = [term for term in tri_dict.keys() if not w2v.get(term) is None]
                        tri_dict_subset = {phrase: tri_dict[phrase] for phrase in phrases}
                        if tri_dict_subset:
                                bigrams.append(tri_dict_subset)
                                for phrase in tri_dict_subset.keys():
                                        if phrase in tri_dict_corpus:
                                                tri_dict_corpus[phrase] = tri_dict_corpus[phrase] + tri_dict_subset[phrase]
                                        else:
                                                tri_dict_corpus[phrase] = tri_dict_subset[phrase]
                                                
                                                
        return bigrams, trigrams, sorted(bi_dict_corpus.items(), key=operator.itemgetter(1), reverse=True)[0:termCount], sorted(tri_dict_corpus.items(), key=operator.itemgetter(1), reverse=True)[0:termCount]

