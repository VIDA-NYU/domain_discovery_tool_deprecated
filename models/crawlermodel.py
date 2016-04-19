import time
import calendar
from datetime import datetime
from dateutil import tz
from sets import Set

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

import numpy as np
from random import random, randint

from subprocess import call
from subprocess import Popen
from subprocess import PIPE

import linecache
from sys import exc_info
from os import chdir, listdir, environ, makedirs, rename, chmod, walk
from os.path import isfile, join, exists, isdir
from zipfile import ZipFile

from elasticsearch import Elasticsearch

from seeds_generator.download import download, decode
from seeds_generator.concat_nltk import get_bag_of_words
from elastic.get_config import get_available_domains, get_mapping, get_tag_colors
from elastic.search_documents import get_context, term_search, search, multifield_term_search, range, multifield_query_search, field_missing, field_exists
from elastic.add_documents import add_document, update_document, refresh
from elastic.get_mtermvectors import getTermStatistics, getTermFrequency
from elastic.get_documents import get_most_recent_documents, get_documents, get_all_ids, get_more_like_this, get_pages_datetimes, get_documents_by_id
from elastic.aggregations import get_significant_terms, get_unique_values
from elastic.create_index import create_index, create_terms_index, create_config_index
from elastic.load_config import load_config
from elastic.create_index import create_config_index
from elastic.config import es, es_doc_type, es_server
from elastic.delete import delete

from ranking import tfidf, rank, extract_terms, word2vec, get_bigrams_trigrams

from topik import read_input, tokenize, vectorize, run_model, visualize, TopikProject

import urllib2
import json

class CrawlerModel:

  w2v = word2vec.word2vec(from_es=False)

  def __init__(self):
    self._es = None
    self._all = 10000
    self._termsIndex = "ddt_terms"
    self._pagesCapTerms = 100
    self._capTerms = 500
    self.projectionsAlg = {'Group by Similarity': self.pca
                           #'t-SNE': self.tsne
                           # 'K-Means': self.kmeans,
                         }

    # TODO(Yamuna): delete when not returning random data anymore.
    self._randomTerms = {
      'Word': ['Word', randint(1, 100), randint(1, 100), ['Positive']],
      'Disease': ['Disease', randint(1, 100), randint(1, 100), ['Negative']],
      'Control': ['Control', randint(1, 100), randint(1, 100), []],
      'Symptoms': ['Symptoms', randint(1, 100), randint(1, 100), ['Positive']],
      'Epidemy': ['Epidemy', 100, 100, []],
    }

    create_config_index()
    create_terms_index()

    self._mapping = {"url":"url", "timestamp":"retrieved", "text":"text", "html":"html", "tag":"tag", "query":"query"}
    self._domains = None
    self.pos_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'FW', 'JJ']
    
  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    # Initializes elastic search.
    self._es = es

    self._domains = get_available_domains(self._es)

    return \
    [{'id': k, 'name': d['domain_name'], 'creation': d['timestamp'], 'index': d['index'], 'doc_type': d['doc_type']} for k, d in self._domains]

  def getAvailableProjectionAlgorithms(self):
    return [{'name': key} for key in self.projectionsAlg.keys()]

  def getAvailablePageRetrievalCriteria(self):
    return [{'name': key} for key in self.pageRetrieval.keys()]

  # Returns a list of available seed crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableSeedCrawlers(self):
    # Initializes elastic search.
    self._es = es
    
    self._domains = get_available_domains(self._es)
    
    return \
    [{'id': k, 'name': d['domain_name'], 'creation': d['timestamp'], 'index': d['index'], 'doc_type': d['doc_type']} for k, d in self._domains.items()]

  def getAvailableQueries(self, session):
    es_info = self.esInfo(session['domainId'])
    return get_unique_values('query', self._all, es_info['activeCrawlerIndex'], es_info['docType'], self._es)

  def getAvailableTags(self, session):
    es_info = self.esInfo(session['domainId'])

    tags_neutral = field_missing("tag", ["url"], self._all, es_info['activeCrawlerIndex'], es_info['docType'], self._es)
    unique_tags = {"Neutral": len(tags_neutral)}

    tags_str = get_unique_values('tag', self._all, es_info['activeCrawlerIndex'], es_info['docType'], self._es)
    for tags, num in tags_str.iteritems():
      tags_list = tags.split(";")
      for tag in tags_list:
        if tag != "":
          if unique_tags.get(tag) is not None:
            unique_tags[tag] = unique_tags[tag] + num
          else:
            unique_tags[tag] = num
        else:
          unique_tags["Neutral"] = unique_tags["Neutral"] + 1
    return unique_tags

  def encode(self, url):
    return urllib2.quote(url).replace("/", "%2F")
    
  def esInfo(self, domainId):
    es_info = {
      "activeCrawlerIndex": self._domains[domainId]['index'],
      "docType": self._domains[domainId]['doc_type']
    }
    if not self._domains[domainId].get("mapping") is None:
      es_info["mapping"] = self._domains[domainId]["mapping"]
    else:
      es_info["mapping"] = self._mapping
    return es_info

  def createModel(self, session):
    es_info = self.esInfo(session['domainId']);

    data_dir = environ["DDT_HOME"] + "/data/"
    data_crawler  = data_dir + es_info['activeCrawlerIndex']
    data_training = data_crawler + "/training_data/"
    data_negative = data_crawler + "/training_data/negative/"
    data_positive = data_crawler + "/training_data/positive/"

    if (not isdir(data_positive)):
      makedirs(data_positive)
    if (not isdir(data_negative)):
      makedirs(data_negative)

    s_fields = {}
    query = {
      "wildcard": {es_info['mapping']["tag"]:"*Relevant*"}
    }
    s_fields["queries"] = [query]
    pos_urls = [field['url'][0] for field in multifield_term_search(s_fields, self._all, ["url", es_info['mapping']['tag']], 
                                    es_info['activeCrawlerIndex'], 
                                    es_info['docType'],
                                    self._es) if "irrelevant" not in field["tag"]]

    query = {
      "wildcard": {es_info['mapping']["tag"]:"*Irrelevant*"}
    }
    s_fields["queries"] = [query]
    neg_urls = [field['url'][0] for field in multifield_term_search(s_fields, self._all, ["url", es_info['mapping']['tag']], 
                                    es_info['activeCrawlerIndex'], 
                                    es_info['docType'],
                                    self._es)]

    pos_html = get_documents(pos_urls, 'url', [es_info['mapping']["html"]], es_info['activeCrawlerIndex'], es_info['docType'])
    neg_html = get_documents(neg_urls, 'url', [es_info['mapping']["html"]], es_info['activeCrawlerIndex'], es_info['docType'])

    seeds_file = data_crawler +"/seeds.txt"
    print "Seeds path ", seeds_file
    with open(seeds_file, 'w') as s:
      for url in pos_html:
        try:
          file_positive = data_positive + self.encode(url.encode('utf8'))
          print file_positive
          s.write(url.encode('utf8') + '\n')
          with open(file_positive, 'w') as f:
            f.write(pos_html[url][0][es_info['mapping']['html']][0])

        except IOError:
          _, exc_obj, tb = exc_info()
          f = tb.tb_frame
          lineno = tb.tb_lineno
          filename = f.f_code.co_filename
          linecache.checkcache(filename)
          line = linecache.getline(filename, lineno, f.f_globals)
          print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

    for url in neg_html:
      try:
        file_negative = data_negative + self.encode(url.encode('utf8'))
        with open(file_negative, 'w') as f:
          f.write(neg_html[url][0]['html'][0])
      except IOError:
        _, exc_obj, tb = exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    
    models_dir = environ["DDT_HOME"] + "/vis/html/models/"
    crawlermodel_dir = models_dir + es_info['activeCrawlerIndex']
    
    if (not isdir(models_dir)):
      makedirs(models_dir)

    if (not isdir(crawlermodel_dir)):
      makedirs(crawlermodel_dir)

    ache_home = environ['ACHE_HOME']
    comm = ache_home + "/bin/ache buildModel -t " + data_training + " -o "+ crawlermodel_dir + " -c " + ache_home + "/config/stoplist.txt"
    p = Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors

    zip_filename = models_dir + es_info['activeCrawlerIndex'] + "_model.zip"
    with ZipFile(zip_filename, "w") as modelzip:
      if (isfile(crawlermodel_dir + "/pageclassifier.features")):
        print "zipping file: "+crawlermodel_dir + "/pageclassifier.features"
        modelzip.write(crawlermodel_dir + "/pageclassifier.features", "pageclassifier.features")
      
      if (isfile(crawlermodel_dir + "/pageclassifier.model")):
        print "zipping file: "+crawlermodel_dir + "/pageclassifier.model"
        modelzip.write(crawlermodel_dir + "/pageclassifier.model", "pageclassifier.model")

      if (exists(data_crawler + "/training_data/positive")):
        print "zipping file: "+ data_crawler + "/training_data/positive"
        for (dirpath, dirnames, filenames) in walk(data_crawler + "/training_data/positive"):
          for html_file in filenames:
            modelzip.write(dirpath + "/" + html_file, "training_data/positive/" + html_file)

      if (exists(data_crawler + "/training_data/negative")):
        print "zipping file: "+ data_crawler + "/training_data/negative"
        for (dirpath, dirnames, filenames) in walk(data_crawler + "/training_data/negative"):
          for html_file in filenames:
            modelzip.write(dirpath + "/" + html_file, "training_data/negative/" + html_file)
        
      if (isfile(data_crawler +"/seeds.txt")):
        print "zipping file: "+data_crawler +"/seeds.txt"
        modelzip.write(data_crawler +"/seeds.txt", es_info['activeCrawlerIndex'] + "_seeds.txt")

    chmod(zip_filename, 0o777)

    return "models/" + es_info['activeCrawlerIndex'] + "_model.zip"


  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # Returns dictionary in the format:
  # {
  #   'Positive': {'Explored': numExploredPages, 'Exploited': numExploitedPages},
  #   'Negative': {'Explored': numExploredPages, 'Exploited': numExploitedPages},
  # }
  def getPagesSummaryCrawler(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False, session = None):
    es_info = self.esInfo(session['domainId'])

    # If ts1 not specified, sets it to -Infinity.
    if opt_ts1 is None:
      now = time.localtime(0)
      opt_ts1 = int(time.mktime(now))
    else:
      opt_ts1 = int(opt_ts1)

    # If ts2 not specified, sets it to now.
    if opt_ts2 is None:
      now = time.localtime()
      opt_ts2 = int(time.mktime(now))
    else:
      opt_ts2 = int(opt_ts2)

    # TODO(Yamuna): Query Elastic Search (schema self._activeCrawlerId) for number of downloaded pages
    # between given Unix epochs.
    # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
    print '\n\n *** init', opt_ts1

    inc = opt_ts2 - opt_ts1

    print '\n\n *** delta', inc

    explored = int(opt_ts1 / 10E6 + inc)
    exploited = int(opt_ts1 / 10E8 + inc / 2)
    boosted = int(opt_ts1 / 10E8 + inc / 2)
    return { \
      'Positive': {'Explored': explored, 'Exploited': exploited, 'Boosted': boosted},
      'Negative': {'Explored': explored / 5, 'Exploited': exploited / 5, 'Boosted':  boosted / 5},
    }



  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # Returns dictionary in the format:
  # {
  #   'Relevant': numRelevantPages,
  #   'Irrelevant': numIrrelevantPages,
  #   'Neutral': numNeutralPages,
  # }
  def getPagesSummarySeedCrawler(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False, session = None):
    es_info = self.esInfo(session['domainId'])

    # If ts1 not specified, sets it to -Infinity.
    if opt_ts1 is None:
      now = time.gmtime(0)
      opt_ts1 = float(calendar.timegm(now))
    else:
      opt_ts1 = float(opt_ts1)

    # If ts2 not specified, sets it to now.
    if opt_ts2 is None:
      now = time.gmtime()
      opt_ts2 = float(calendar.timegm(now))
    else:
      opt_ts2 = float(opt_ts2)

    if opt_applyFilter and session['filter'] != "":
      results = get_most_recent_documents(session['pagesCap'], es_info['mapping'], ["url", es_info['mapping']["tag"]], 
                                          session['filter'], es_info['activeCrawlerIndex'], es_info['docType'],  \
                                          self._es)
    else:
      results = \
      range(es_info['mapping']["timestamp"], opt_ts1, opt_ts2, ['url',es_info['mapping']['tag']], True, session['pagesCap'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)

    relevant = 0
    irrelevant = 0
    neutral = 0

    for res in results:
        try:
          tags = res[es_info['mapping']['tag']]
          if 'Irrelevant' in res[es_info['mapping']['tag']]:
            irrelevant = irrelevant + 1
          else:
            # Page has tags Relevant or custom.
            if "" not in tags:
              relevant = relevant + 1
            else:
              neutral = neutral + 1
        except KeyError:
          # Page does not have tags.
          neutral = neutral + 1

    return { \
      'Relevant': relevant,
      'Irrelevant': irrelevant,
      'Neutral': neutral
    }

  # Returns number of terms present in positive and negative pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInPositivePages, frequencyInNegativePages, tags],
  #   [term, frequencyInPositivePages, frequencyInNegativePages, tags],
  #   ...
  # ]
  def getTermsSummaryCrawler(self, opt_maxNumberOfeTerms = 50, session = None):
    # TODO(Yamuna): Query Elastic Search (schema self._activeCrawlerId) for terms ranked by highest
    # tf-idf, and return top opt_maxNumberOfTerms, with tf_idf for term occurring in positive and
    # negative pages.
    #return 9 * [e[:3] for e in self._randomTerms.values()]
    return 9 * self._randomTerms.values()



  # Returns number of terms present in relevant and irrelevant pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInRelevantPages, frequencyInIrrelevantPages, tags],
  #   [term, frequencyInRelevantPages, frequencyInIrrelevantPages, tags],
  #   ...
  # ]
  def getTermsSummarySeedCrawler(self, opt_maxNumberOfTerms = 40, session = None):

    es_info = self.esInfo(session['domainId'])

    format = '%m/%d/%Y %H:%M %Z'
    if not session['fromDate'] is None:
      session['fromDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['fromDate'], format)) * 1000)
    if not session['toDate'] is None:
      session['toDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['toDate'], format)) * 1000)

    s_fields = {
      "tag": "Positive",
      "index": es_info['activeCrawlerIndex'],
      "doc_type": es_info['docType']
    }

    pos_terms = [field['term'][0] for field in multifield_term_search(s_fields, self._capTerms, ['term'], self._termsIndex, 'terms', self._es)]
        
    s_fields["tag"]="Negative"
    neg_terms = [field['term'][0] for field in multifield_term_search(s_fields, self._capTerms, ['term'], self._termsIndex, 'terms', self._es)]

    results = self.getPagesQuery(session)

    top_terms = []
    top_bigrams = []
    top_trigrams = []

    
    text = []
    urls = [hit["id"] for hit in results if (hit.get(es_info['mapping']["tag"]) is not None) and ("Relevant" in hit[es_info['mapping']["tag"]])]
    if(len(urls) > 0):
      text = [hit[es_info['mapping']["text"]][0] for hit in results if (hit.get(es_info['mapping']["tag"]) is not None) and ("Relevant" in hit[es_info['mapping']["tag"]])]
    else:
      urls = [hit["id"] for hit in results]
      # If positive urls are not available then get the most recent documents
      text = [hit[es_info['mapping']["text"]][0] for hit in results]

    from nltk import corpus
    ENGLISH_STOPWORDS = corpus.stopwords.words('english')

    if session["filter"] == "" or session["filter"] is None:
      if len(urls) > 0:
        [bigram_tfidf_data, trigram_tfidf_data,_,_,bigram_corpus, trigram_corpus,_,_,top_bigrams, top_trigrams] = get_bigrams_trigrams.get_bigrams_trigrams(text, urls, opt_maxNumberOfTerms+len(neg_terms), self.w2v, self._es)
         
        tfidf_all = tfidf.tfidf(urls, pos_tags=self.pos_tags, mapping=es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
        if pos_terms:
          extract_terms_all = extract_terms.extract_terms(tfidf_all)
          [ranked_terms, scores] = extract_terms_all.results(pos_terms)
          top_terms = [ term for term in ranked_terms if (term not in neg_terms)]
          top_terms = top_terms[0:opt_maxNumberOfTerms]

          tfidf_bigram = tfidf.tfidf()
          tfidf_bigram.tfidfArray = bigram_tfidf_data
          tfidf_bigram.opt_docs = urls
          tfidf_bigram.corpus = bigram_corpus
          tfidf_bigram.mapping = es_info['mapping']
          extract_terms_all = extract_terms.extract_terms(tfidf_bigram)
          [ranked_terms, scores] = extract_terms_all.results(pos_terms)
          top_bigrams = [ term for term in ranked_terms if (term not in neg_terms)]

          tfidf_trigram = tfidf.tfidf()
          tfidf_trigram.tfidfArray = trigram_tfidf_data
          tfidf_trigram.opt_docs = urls
          tfidf_trigram.corpus = trigram_corpus
          tfidf_trigram.mapping = es_info['mapping']
          extract_terms_all = extract_terms.extract_terms(tfidf_trigram)
          [ranked_terms, scores] = extract_terms_all.results(pos_terms)
          top_trigrams = [ term for term in ranked_terms if (term not in neg_terms)]
          top_trigrams = top_trigrams[0:opt_maxNumberOfTerms]
        else:
          top_terms = [term for term in tfidf_all.getTopTerms(opt_maxNumberOfTerms+len(neg_terms)) if (term not in neg_terms)]
          top_bigrams = [term for term in top_bigrams if term not in neg_terms]
          top_trigrams = [term for term in top_trigrams if term not in neg_terms]
    else:
      top_terms = [term for term in get_significant_terms(urls, opt_maxNumberOfTerms+len(neg_terms), mapping=es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es) if (term not in neg_terms)]
      if len(text) > 0:
        [_,_,_,_,_,_,_,_,top_bigrams, top_trigrams] = get_bigrams_trigrams.get_bigrams_trigrams(text, urls, opt_maxNumberOfTerms+len(neg_terms), self.w2v, self._es)
        top_bigrams = [term for term in top_bigrams if term not in neg_terms]
        top_trigrams = [term for term in top_trigrams if term not in neg_terms]

    count = 0
    bigrams = top_bigrams
    top_bigrams = []
    for phrase in bigrams:
      words = phrase.split(" ")
      if words[0] not in ENGLISH_STOPWORDS and words[1] not in ENGLISH_STOPWORDS and count <= opt_maxNumberOfTerms:
        count = count + 1
        top_bigrams.append(phrase)

    s_fields = {
      "tag": "Custom",
      "index": es_info['activeCrawlerIndex'],
      "doc_type": es_info['docType']
    }

    custom_terms = [field['term'][0] for field in multifield_query_search(s_fields, 500, ['term'], self._termsIndex, 'terms', self._es)]

    top_terms = custom_terms + top_terms

    if not top_terms:  
      return []

    pos_freq = {}
    pos_data = {field['id']:field['text'][0] for field in term_search(es_info['mapping']['tag'], ['Relevant'], self._all, ['url', 'text'], es_info['activeCrawlerIndex'], es_info['docType'], self._es)}
    pos_urls = pos_data.keys();
    pos_text = pos_data.values();
    if len(pos_urls) > 1:
      tfidf_pos = tfidf.tfidf(pos_urls, pos_tags=self.pos_tags, mapping=es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
      [_,corpus,ttfs_pos] = tfidf_pos.getTfArray()
      
      total_pos_tf = np.sum(ttfs_pos, axis=0)
      total_pos = np.sum(total_pos_tf)

      [_,_,bigram_tf_data,trigram_tf_data,bigram_corpus, trigram_corpus,_,_,_,_] = get_bigrams_trigrams.get_bigrams_trigrams(pos_text, pos_urls, opt_maxNumberOfTerms, self.w2v, self._es)

      total_bigram_pos_tf = np.sum(bigram_tf_data, axis=0)
      total_bigram_pos = np.sum(total_bigram_pos_tf)

      total_trigram_pos_tf = np.sum(trigram_tf_data, axis=0)
      total_trigram_pos = np.sum(total_trigram_pos_tf)

      pos_freq={}
      for key in top_terms:
        try:
          pos_freq[key] = (float(total_pos_tf[corpus.index(key)])/total_pos)
        except ValueError:
          if key not in custom_terms:
            pos_freq[key] = 0
        
      for key in top_bigrams + custom_terms:
        try:
          pos_freq[key] = (float(total_bigram_pos_tf[bigram_corpus.index(key)])/total_bigram_pos)
        except ValueError:
          if key not in custom_terms:
            pos_freq[key] = 0
          
      for key in top_trigrams + custom_terms:
        try:
          pos_freq[key] = (float(total_trigram_pos_tf[trigram_corpus.index(key)])/total_trigram_pos)
        except ValueError:
          if key not in custom_terms:
            pos_freq[key] = 0

      for term in custom_terms:
        if pos_freq.get(term) == None:
          pos_freq[term] = 0
    else:
      pos_freq = { key: 0 for key in top_terms }
      pos_freq = { key: 0 for key in top_bigrams }
      pos_freq = { key: 0 for key in top_trigrams }      
      pos_freq = { key: 0 for key in custom_terms }
      
    neg_data = {field['id']:field['text'][0] for field in term_search(es_info['mapping']['tag'], ['Irrelevant'], self._all, ['url', 'text'], es_info['activeCrawlerIndex'], es_info['docType'], self._es)}
    neg_urls = neg_data.keys();
    neg_text = neg_data.values();

    neg_freq = {}
    if len(neg_urls) > 1:
      tfidf_neg = tfidf.tfidf(neg_urls, pos_tags=self.pos_tags, mapping=es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
      [_,corpus,ttfs_neg] = tfidf_neg.getTfArray()
      total_neg_tf = np.sum(ttfs_neg, axis=0)
      total_neg = np.sum(total_neg_tf)

      [_,_,bigram_tf_data,trigram_tf_data,bigram_corpus, trigram_corpus,_,_,_,_] = get_bigrams_trigrams.get_bigrams_trigrams(neg_text, neg_urls, opt_maxNumberOfTerms, self.w2v, self._es)

      total_bigram_neg_tf = np.sum(bigram_tf_data, axis=0)
      total_bigram_neg = np.sum(total_bigram_neg_tf)

      total_trigram_neg_tf = np.sum(trigram_tf_data, axis=0)
      total_trigram_neg = np.sum(total_trigram_neg_tf)

      neg_freq={}
      for key in top_terms + custom_terms:
        try:
          neg_freq[key] = (float(total_neg_tf[corpus.index(key)])/total_neg)
        except ValueError:
          if key not in custom_terms:
            neg_freq[key] = 0

      for key in top_bigrams + custom_terms:
        try:
          neg_freq[key] = (float(total_bigram_neg_tf[bigram_corpus.index(key)])/total_bigram_neg)
        except ValueError:
          if key not in custom_terms:
            neg_freq[key] = 0
          
      for key in top_trigrams + custom_terms:
        try:
          neg_freq[key] = (float(total_trigram_neg_tf[trigram_corpus.index(key)])/total_trigram_neg)
        except ValueError:
          if key not in custom_terms:
            neg_freq[key] = 0

      for term in custom_terms:
        if neg_freq.get(term) == None:
          neg_freq[term] = 0
    
    else:
      neg_freq = { key: 0 for key in top_terms }      
      neg_freq = { key: 0 for key in top_bigrams }      
      neg_freq = { key: 0 for key in top_trigrams }
      neg_freq = { key: 0 for key in custom_terms }      
      
    terms = []

    s_fields = {
      "term": "",
      "index": es_info['activeCrawlerIndex'],
      "doc_type": es_info['docType'],
    }

    results = []
    for term in top_terms:
      s_fields["term"] = term
      res = multifield_term_search(s_fields, self._capTerms, ['tag', 'term'], self._termsIndex, 'terms', self._es)
      results.extend(res)

    tags = {result['term'][0]: result['tag'][0] for result in results}    

    for term in top_terms:
      try:
        term_pos_freq = pos_freq[term]
      except KeyError:
        term_pos_freq = 0
      try:
        term_neg_freq = neg_freq[term]
      except KeyError:
        term_neg_freq = 0
      entry = [term, term_pos_freq, term_neg_freq, []]

      if tags and not tags.get(term) is None:
        entry[3] = tags[term].split(';')
      terms.append(entry)
      
    for term in top_bigrams:
      try:
        term_pos_freq = pos_freq[term]
      except KeyError:
        term_pos_freq = 0
      try:
        term_neg_freq = neg_freq[term]
      except KeyError:
        term_neg_freq = 0

      entry = [term, term_pos_freq, term_neg_freq, []]
      terms.append(entry)

    for term in top_trigrams:
      try:
        term_pos_freq = pos_freq[term]
      except KeyError:
        term_pos_freq = 0
      try:
        term_neg_freq = neg_freq[term]
      except KeyError:
        term_neg_freq = 0

      entry = [term, term_pos_freq, term_neg_freq, []]
      terms.append(entry)
    
    return terms

  # Sets limit to pages returned by @getPages.
  def setPagesCountCap(self, pagesCap):
    self._pagesCap = int(pagesCap)


  def _getMostRecentPages(self, session):
    es_info = self.esInfo(session['domainId'])

    hits = []
    if session['fromDate'] is None:
      hits = get_most_recent_documents(session['pagesCap'], es_info['mapping'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]],  
                                       session['filter'],
                                       es_info['activeCrawlerIndex'],
                                       es_info['docType'],
                                       self._es)
    else:
      if(session['filter'] is None):
        hits = range(es_info['mapping']["timestamp"], session['fromDate'], session['toDate'], ['url',"x", "y", es_info['mapping']['tag'], es_info['mapping']["timestamp"], es_info['mapping']["text"]], True, session['pagesCap'], 
                     es_info['activeCrawlerIndex'], 
                     es_info['docType'], 
                     self._es)
      else:
        s_fields = {
          es_info['mapping']["text"]: "(" + session['filter'].replace('"','\"') + ")",
          es_info['mapping']["timestamp"]: "[" + str(session['fromDate']) + " TO " + str(session['toDate']) + "]" 
        }
        hits = multifield_query_search(s_fields, session['pagesCap'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], 
                                       es_info['activeCrawlerIndex'], 
                                       es_info['docType'],
                                       self._es)
    return hits

  def _getPagesForQueries(self, session):
    es_info = self.esInfo(session['domainId'])

    s_fields = {}
    if not session['filter'] is None:
      s_fields[es_info['mapping']["text"]] =   session['filter'].replace('"','\"')

    if not session['fromDate'] is None:
      s_fields[es_info['mapping']["timestamp"]] = "[" + str(session['fromDate']) + " TO " + str(session['toDate']) + "]" 
      
    hits=[]
    queries = session['selected_queries'].split(',')
    for query in queries:
      s_fields[es_info['mapping']["query"]] = '"' + query + '"'
      results= multifield_query_search(s_fields, session['pagesCap'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], 
                                       es_info['activeCrawlerIndex'], 
                                       es_info['docType'],
                                      self._es)
      hits.extend(results)
    return hits

  def _getPagesForTags(self, session):
    es_info = self.esInfo(session['domainId'])

    s_fields = {}
    if not session['filter'] is None:
      s_fields[es_info['mapping']["text"]] = session['filter'].replace('"','\"')

    if not session['fromDate'] is None:
      s_fields[es_info['mapping']["timestamp"]] = "[" + str(session['fromDate']) + " TO " + str(session['toDate']) + "]" 
      
    hits=[]
    tags = session['selected_tags'].split(',')
    for tag in tags:
      if tag != "":
        if tag == "Neutral":
          query_field_missing = {
            "filtered" : {
              "filter" : {
                "missing" : { "field" : "tag" }
              }
            }
          }

          s_fields["queries"] = [query_field_missing]

          results = multifield_term_search(s_fields, session['pagesCap'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], 
                                           es_info['activeCrawlerIndex'], 
                                           es_info['docType'],
                                           self._es)

          hits.extend(results)
          
          s_fields["tag"] = ""

          results = multifield_term_search(s_fields, session['pagesCap'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], 
                                           es_info['activeCrawlerIndex'], 
                                           es_info['docType'],
                                           self._es)

          hits.extend(results)
          
          s_fields.pop("tag")

        else:  
          #Added a wildcard query as tag is not analyzed field
          query = {
            "wildcard": {es_info['mapping']["tag"]:"*" + tag + "*"}
          }
          s_fields["queries"] = [query]
          results= multifield_term_search(s_fields, session['pagesCap'], ["url", "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], 
                                          es_info['activeCrawlerIndex'], 
                                          es_info['docType'],
                                          self._es)
          hits.extend(results)
        
    return hits

  def _getRelevantPages(self, session):
    es_info = self.esInfo(session['domainId'])

    pos_hits = search(es_info['mapping']['tag'], ['relevant'], session['pagesCap'], ['url', "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], es_info['activeCrawlerIndex'], 'page', self._es)

    return pos_hits

  def _getMoreLikePages(self, session):
    es_info = self.esInfo(session['domainId'])
    
    hits=[]
    tags = session['selected_tags'].split(',')
    for tag in tags:
      tag_hits = search(es_info['mapping']['tag'], [tag], session['pagesCap'], ['url', "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], es_info['activeCrawlerIndex'], 'page', self._es)

      if len(tag_hits) > 0:
        tag_urls = [field['id'] for field in tag_hits]
      
        results = get_more_like_this(tag_urls, ['url', "x", "y", es_info['mapping']["tag"], es_info['mapping']["timestamp"], es_info['mapping']["text"]], session['pagesCap'],  es_info['activeCrawlerIndex'], es_info['docType'],  self._es)
      
        hits.extend(tag_hits[0:self._pagesCapTerms] + results)

    return hits

  def getPagesQuery(self, session):
    es_info = self.esInfo(session['domainId'])
    
    format = '%m/%d/%Y %H:%M %Z'
    if not session['fromDate'] is None:
      session['fromDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['fromDate'], format)))

    if not session['toDate'] is None:
      session['toDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['toDate'], format)))

    hits = []
    if(session['pageRetrievalCriteria'] == 'Most Recent'):
      hits = self._getMostRecentPages(session)
    elif (session['pageRetrievalCriteria'] == 'Queries'):
      hits = self._getPagesForQueries(session)
    elif (session['pageRetrievalCriteria'] == 'Tags'):
      hits = self._getPagesForTags(session)
    elif (session['pageRetrievalCriteria'] == 'More like'):
      hits = self._getMoreLikePages(session)

    return hits  

  # Returns most recent downloaded pages.
  # Returns dictionary in the format:
  # {
  #   'last_downloaded_url_epoch': 1432310403 (in seconds)
  #   'pages': [
  #             [url1, x, y, tags, retrieved],     (tags are a list, potentially empty)
  #             [url2, x, y, tags, retrieved],
  #             [url3, x, y, tags, retrieved],
  #   ]
  # }
  def getPages(self, session):

    es_info = self.esInfo(session['domainId'])
    
    format = '%m/%d/%Y %H:%M %Z'
    if not session['fromDate'] is None:
      session['fromDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['fromDate'], format)))

    if not session['toDate'] is None:
      session['toDate'] = long(CrawlerModel.convert_to_epoch(datetime.strptime(session['toDate'], format)))

    hits = self.getPagesQuery(session)

    last_downloaded_url_epoch = None
    docs = []

    for i, hit in enumerate(hits):
      if last_downloaded_url_epoch is None:
        if not hit.get(es_info['mapping']['timestamp']) is None:
          last_downloaded_url_epoch = str(hit[es_info['mapping']['timestamp']][0])

      doc = ["", 0, 0, [], "", ""]

      if not hit.get('url') is None:  
        doc[0] = hit.get('url')
      if not hit.get('x') is None:
        doc[1] = hit['x'][0]
      if not hit.get('y') is None:
        doc[2] = hit['y'][0]
      if not hit.get(es_info['mapping']['tag']) is None:
        doc[3] = hit[es_info['mapping']['tag']][0].split(';')
      if not hit.get('id') is None:
        doc[4] = hit['id']
      if not hit.get(es_info['mapping']["text"]) is None:
        doc[5] = hit[es_info['mapping']["text"]][0]
        
      docs.append(doc)

    if len(docs) > 1:
      # Prepares results: computes projection.
      # Update x, y for pages after projection is done.
      projectionData = self.projectPages(docs, session['activeProjectionAlg'])

      last_download_epoch = last_downloaded_url_epoch
      try:  
        format = '%Y-%m-%dT%H:%M:%S.%f'
        if '+' in last_downloaded_url_epoch:
          format = '%Y-%m-%dT%H:%M:%S+0000'
        last_download_epoch = CrawlerModel.convert_to_epoch(datetime.strptime(last_downloaded_url_epoch, format))
      except ValueError:
        try:
          format = '%Y-%m-%d %H:%M:%S.%f'
          last_download_epoch = CrawlerModel.convert_to_epoch(datetime.strptime(last_downloaded_url_epoch, format))
        except ValueError:
          pass

      return {\
              'last_downloaded_url_epoch':  last_download_epoch,
              'pages': projectionData
            }
    elif len(docs) == 1:
      doc = docs[0]
      return {'pages': [[doc[0],1,1,doc[3]]]}
    else:
      return {'pages': []}

  # Boosts set of pages: crawler exploits outlinks for the given set of pages in active crawler.
  def boostPages(self, pages):
    # TODO(Yamuna): Issue boostPages on running crawler defined by active crawlerId.
    i = 0
    print 3 * '\n', 'boosted pages', str(pages), 3 * '\n'

  # Fetches snippets for a given term.
  def getTermSnippets(self, term, session):
    es_info = self.esInfo(session['domainId'])

    #tags = get_documents(term, 'term', ['tag'], es_info['activeCrawlerIndex'], 'terms', self._es)


    s_fields = {
      "term": term,
      "index": es_info['activeCrawlerIndex'],
      "doc_type": es_info['docType'],
    }

    tags = multifield_term_search(s_fields, self._capTerms, ['tag'], self._termsIndex, 'terms', self._es)
    
    tag = []
    if tags:
      tag = tags[0]['tag'][0].split(';')

    return {'term': term, 'tags': tag, 'context': get_context(term.split('_'), es_info['mapping']['text'], es_info['activeCrawlerIndex'], es_info['docType'],  self._es)}

  # Crawl forward
  def getForwardLinks(self, urls, session):

    es_info = self.esInfo(session['domainId'])
    
    results = field_exists("crawled_forward", [es_info['mapping']['url']], self._all, es_info['activeCrawlerIndex'], es_info['docType'], self._es)    
    already_crawled = [result[es_info["mapping"]["url"]][0] for result in results]
    not_crawled = list(Set(urls).difference(already_crawled))
    results = get_documents(not_crawled, es_info["mapping"]['url'], [es_info["mapping"]['url']], es_info['activeCrawlerIndex'], es_info['docType'], self._es)    
    not_crawled_urls = [results[url][0][es_info["mapping"]["url"]][0] for url in not_crawled]
    
    chdir(environ['DDT_HOME']+'/seeds_generator')
    
    comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar StartCrawl -c forward"\
           " -u \"" + ",".join(not_crawled_urls) + "\"" + \
           " -t " + session["pagesCap"] + \
           " -i " + es_info['activeCrawlerIndex'] + \
           " -d " + es_info['docType'] + \
           " -s " + es_server 
    
    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors

  # Crawl backward
  def getBackwardLinks(self, urls, session):

    es_info = self.esInfo(session['domainId'])
    
    results = field_exists("crawled_backward", [es_info['mapping']['url']], self._all, es_info['activeCrawlerIndex'], es_info['docType'], self._es)    
    already_crawled = [result[es_info["mapping"]["url"]][0] for result in results]
    not_crawled = list(Set(urls).difference(already_crawled))
    results = get_documents(not_crawled, es_info["mapping"]['url'], [es_info["mapping"]['url']], es_info['activeCrawlerIndex'], es_info['docType'], self._es)
    not_crawled_urls = [results[url][0][es_info["mapping"]["url"]][0] for url in not_crawled]

    chdir(environ['DDT_HOME']+'/seeds_generator')
        
    comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar StartCrawl -c backward"\
           " -u \"" + ",".join(not_crawled_urls) + "\"" + \
           " -t " + session["pagesCap"] + \
           " -i " + es_info['activeCrawlerIndex'] + \
           " -d " + es_info['docType'] + \
           " -s " + es_server 
    
    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors
                         
    
  # Adds tag tow pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  def setPagesTag(self, pages, tag, applyTagFlag, session):
    
    es_info = self.esInfo(session['domainId'])

    entries = {}
    results = get_documents(pages, 'url', [es_info['mapping']['tag']], es_info['activeCrawlerIndex'], es_info['docType'],  self._es)

    if applyTagFlag and len(results) > 0:
      print '\n\napplied tag ' + tag + ' to pages' + str(pages) + '\n\n'
      
      for page in pages:
        if not results.get(page) is None:
          # pages to be tagged exist
          records = results[page]
          for record in records:
            entry = {}
            if record.get(es_info['mapping']['tag']) is None:
              # there are no previous tags
              entry[es_info['mapping']['tag']] = tag
            else:
              current_tag = record[es_info['mapping']['tag']][0]
              tags = []
              if  current_tag != '':
                # all previous tags were removed
                tags = list(set(current_tag.split(';')))
                
              if len(tags) != 0:
                # previous tags exist
                if not tag in tags:
                  # append new tag    
                  entry[es_info['mapping']['tag']] = ';'.join(tags)+';'+tag
              else:
                # add new tag
                entry[es_info['mapping']['tag']] = tag

            if entry:
                  entries[record['id']] =  entry

    elif len(results) > 0:
      print '\n\nremoved tag ' + tag + ' from pages' + str(pages) + '\n\n'

      for page in pages:
        if not results.get(page) is None:
          records = results[page]
          for record in records:
            entry = {}
            if not record.get(es_info['mapping']['tag']) is None:
              current_tag = record[es_info['mapping']['tag']][0]
              if tag in current_tag:
                tags = list(set(current_tag.split(';')))
                tags.remove(tag)
                entry[es_info['mapping']['tag']] = ';'.join(tags)
                entries[record['id']] = entry
    
    if entries:
      update_try = 0
      while (update_try < 10):
        try:
          update_document(entries, es_info['activeCrawlerIndex'], es_info['docType'], self._es)
          break
        except:
          update_try = update_try + 1

        
  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag, session):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.

    es_info = self.esInfo(session['domainId'])

    s_fields = {
      "term": "",
      "index": es_info['activeCrawlerIndex'],
      "doc_type": es_info['docType'],
    }

    tags = []
    for term in terms:
      s_fields["term"] = term
      res = multifield_term_search(s_fields, 1, ['tag'], self._termsIndex, 'terms', self._es)
      tags.extend(res)

    results = {result['id']: result['tag'][0] for result in tags}

    add_entries = []
    update_entries = {}

    if applyTagFlag:
      for term in terms:
        if len(results) > 0:
          if results.get(term) is None:
            entry = {
              "term" : term,
              "tag" : tag,
              "index": es_info['activeCrawlerIndex'],
              "doc_type": es_info['docType'],
              "_id" : term+'_'+es_info['activeCrawlerIndex']+'_'+es_info['docType']
            }
            add_entries.append(entry)
          else:
            old_tag = results[term]
            if tag not in old_tag:
              entry = {
                "term" : term,
                "tag" : tag,
                "index": es_info['activeCrawlerIndex'],
                "doc_type": es_info['docType'],
              }
              update_entries[term+'_'+es_info['activeCrawlerIndex']+'_'+es_info['docType']] = entry
        else:
          entry = {
            "term" : term,
            "tag" : tag,
            "index": es_info['activeCrawlerIndex'],
            "doc_type": es_info['docType'],
            "_id": term+'_'+es_info['activeCrawlerIndex']+'_'+es_info['docType']
          }
          add_entries.append(entry)
    else:
      for term in terms:
        if len(results) > 0:
          if not results.get(term) is None:
            if tag in results[term]:
              entry = {
                "term" : term,
                "tag" : "",
                "index": es_info['activeCrawlerIndex'],
                "doc_type": es_info['docType']
              }
              update_entries[term+'_'+es_info['activeCrawlerIndex']+'_'+es_info['docType']] = entry

    if add_entries:
      add_document(add_entries, self._termsIndex, 'terms', self._es)
    
    if update_entries:
      update_document(update_entries, self._termsIndex, 'terms', self._es)

  # Delete terms from term window and from the ddt_terms index
  def deleteTerm(self,term, session):
    es_info = self.esInfo(session['domainId'])
    delete([term+'_'+es_info['activeCrawlerIndex']+'_'+es_info['docType']], self._termsIndex, "terms", self._es)    

  # Add crawler
  def addCrawler(self, index_name):

    create_index(index_name, es=self._es)
    
    fields = index_name.lower().split(' ')
    index = '_'.join([item for item in fields if item not in ''])
    index_name = ' '.join([item for item in fields if item not in ''])
    entry = { "domain_name": index_name.title(),
              "index": index,
              "doc_type": "page",
              "timestamp": datetime.utcnow(),
            }

    load_config([entry])

  def updateColors(self, session, colors):
    es_info = self.esInfo(session['domainId'])

    entry = {
      session['domainId']: {
        "colors": colors["colors"],
        "index": colors["index"] 
      }
    }
    
    update_document(entry, "config", "tag_colors", self._es)

  def getTagColors(self, domainId):
    tag_colors = get_tag_colors(self._es).get(domainId)

    colors = None
    if tag_colors is not None:
      colors = {"index": tag_colors["index"]}
      colors["colors"] = {}
      for color in tag_colors["colors"]:
        fields  = color.split(";")
        colors["colors"][fields[0]] = fields[1]

    return colors
    
  # Submits a web query for a list of terms, e.g. 'ebola disease'
  def queryWeb(self, terms, max_url_count = 100, session = None):
    # TODO(Yamuna): Issue query on the web: results are stored in elastic search, nothing returned
    # here.
    
    es_info = self.esInfo(session['domainId'])

    chdir(environ['DDT_HOME']+'/seeds_generator')
    
    if(int(session['pagesCap']) <= max_url_count):
      top = int(session['pagesCap'])
    else:
      top = max_url_count

    if 'GOOG' in session['search_engine']:
      comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar GoogleSearch -t " + str(top) + \
             " -q \"" + terms + "\"" + \
             " -i " + es_info['activeCrawlerIndex'] + \
             " -d " + es_info['docType'] + \
             " -s " + es_server
    elif 'BING' in session['search_engine']:
      comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar BingSearch -t " + str(top) + \
             " -q \"" + terms + "\"" + \
             " -i " + es_info['activeCrawlerIndex'] + \
             " -d " + es_info['docType'] + \
             " -s " + es_server

    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors

  # Download the pages of uploaded urls
  def downloadUrls(self, urls, session):  
    es_info = self.esInfo(session['domainId'])

    chdir(environ['DDT_HOME']+'/seeds_generator')
    
    comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar Download_urls -u \"" + urls + "\"" \
           " -i " + es_info['activeCrawlerIndex'] + \
           " -d " + es_info['docType'] + \
           " -s " + es_server 

    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors

  def getPagesDates(self, session):
    es_info = self.esInfo(session['domainId'])
    return get_pages_datetimes(es_info["activeCrawlerIndex"])
    
  # Projects pages.
  def projectPages(self, pages, projectionType='TSNE'):
    return self.projectionsAlg[projectionType](pages)
    
  # Projects pages with PCA
  def pca(self, pages):
    
    urls = [page[4] for page in pages]
    text = [page[5] for page in pages]

    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #[urls, data] = CrawlerModel.w2v.process(urls, es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
  
    [urls, data] = CrawlerModel.w2v.process_text(urls, text)

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    pca_count = 2
    pcadata = CrawlerModel.runPCASKLearn(data, pca_count)

    try:
      results = []
      i = 0
      for page in pages:
        if page[4] in urls:
          pdata = [page[0], pcadata[1][i][0], pcadata[1][i][1], page[3]]
          i = i + 1
          results.append(pdata)
    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i

    return results

  # Projects pages with TSNE
  def tsne(self, pages):
    
    urls = [page[4] for page in pages]
    text = [page[5] for page in pages]
    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    #[urls, data] = CrawlerModel.w2v.process(urls, es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
    [urls, data] = CrawlerModel.w2v.process_text(urls, text)
    
    tsne_count = 2
    tsnedata = CrawlerModel.runTSNESKLearn(data, tsne_count)

    try:
      results = []
      i = 0
      for page in pages:
        if page[4] in urls:
          pdata = [page[0], tsnedata[1][i][0], tsnedata[1][i][1], page[3]]
          i = i + 1
          results.append(pdata)

    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i
    return results

  # Projects pages with KMeans
  def kmeans(self, pages):
    
    urls = [page[4] for page in pages]
    text = [page[5] for page in pages]

    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    #[urls, data] = CrawlerModel.w2v.process(urls, es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
    [urls, data] = CrawlerModel.w2v.process_text(urls, text)

    k = 5
    kmeansdata = CrawlerModel.runKMeansSKLearn(data, k)

    try:
      results = []
      i = 0
      for page in pages:
        if page[4] in urls:
          pdata = [page[0], kmeansdata[1][i][0], kmeansdata[1][i][1], page[3]]
          i = i + 1
          results.append(pdata)

    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i
    return results

  def term_tfidf(self, urls):
    [data, data_tf, data_ttf , corpus, urls] = getTermStatistics(urls, mapping=es_info['mapping'], es_index=es_info['activeCrawlerIndex'], es_doc_type=es_info['docType'], es=self._es)
    return [data, data_tf, data_ttf, corpus, urls]

  @staticmethod
  def runPCASKLearn(X, pc_count = None):
    pca = PCA(n_components=pc_count)
    #pca.fit(X)
    #return [pca.explained_variance_ratio_.tolist(), pca.fit_transform(X).tolist()]
    return [None, pca.fit_transform(X).tolist()]

  @staticmethod
  def runTSNESKLearn(X, pc_count = None):
    tsne = TSNE(n_components=pc_count, random_state=0)
    return [None, tsne.fit_transform(X).tolist()]

  @staticmethod
  def runKMeansSKLearn(X, k = None):
    kmeans = KMeans(n_clusters=k, n_jobs=-1)
    clusters = kmeans.fit_predict(X).tolist()
    cluster_distance = kmeans.fit_transform(X).tolist()
    cluster_centers = kmeans.cluster_centers_

    coords = []
    for cluster in clusters:
      coord = [cluster_centers[cluster,0], cluster_centers[cluster, 1]]
      coords.append(coord)

    return [None, coords]

  @staticmethod
  def convert_to_epoch(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

  def make_topic_model(self, domain, tokenizer, vectorizer, model, ntopics):
    """Build topic model from the corpus of the supplied DDT domain.

    The topic model is represented as a topik.TopikProject object, and is
    persisted in disk, recording the model parameters and the location of the
    data. The output of the topic model itself is stored in Elasticsearch.

    Parameters
    ----------
    domain: str
        DDT domain name as stored in Elasticsearch, so lowercase and with underscores in place of spaces.
    tokenizer: str
        A tokenizer from ``topik.tokenizer.registered_tokenizers``
    vectorizer: str
        A vectorization method from ``topik.vectorizers.registered_vectorizers``
    model: str
        A topic model from ``topik.vectorizers.registered_models``
    ntopics: int
        The number of topics to be used when modeling the corpus.

    Returns
    -------
    model: a topik topic model
        A topik model, encoding things like term frequencies, etc.
    """
    content_field = 'text'
    def not_empty(doc): return bool(doc[content_field])  # True if document not empty
    raw_data = filter(not_empty, read_input(source="http://localhost:9200", index=domain))
    id_doc_pairs = ((hash(__[content_field]), __[content_field]) for __ in raw_data)
    tokens = tokenize(id_doc_pairs, method=tokenizer)
    vectors = vectorize(tokens, method=vectorizer)
    model = run_model(vectors, model_name=model, ntopics=ntopics)
    return model


