import time
from datetime import datetime
from pprint import pprint

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
from elastic.get_config import get_available_domains, get_mapping
from elastic.search_documents import get_context, term_search, search, multifield_term_search, range 
from elastic.add_documents import add_document, update_document, refresh
from elastic.get_mtermvectors import getTermStatistics, getTermFrequency
from elastic.get_documents import get_most_recent_documents, get_documents, get_all_ids, get_more_like_this, get_documents_by_id
from elastic.aggregations import get_significant_terms
from elastic.create_index import create_index, create_terms_index, create_config_index
from elastic.load_config import load_config
from elastic.create_index import create_config_index
from elastic.config import es, es_doc_type, es_server

from ranking import tfidf, rank, extract_terms, word2vec

import urllib2
import json

class CrawlerModel:

  w2v = word2vec.word2vec()

  def __init__(self):
    self.es = None
    self._activeCrawlerIndex = None
    self._activeCrawlerId = None
    self._termsIndex = "ddt_terms"
    self._activeProjectionAlg = None
    self._docType = None
    self._filter = None
    self._pagesCap = 100
    self._pagesCapTerms = 50
    self.projectionsAlg = {'PCA': self.pca,
                           't-SNE': self.tsne,
                           'K-Means': self.kmeans,
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

    self._mapping = {"timestamp": "retrieved", "text": "text", "html":"html", "tag":"tag"}
    self._domains = None

    
  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    # Initializes elastic search.
    self.es = es

    self._domains = get_available_domains(self.es)

    return \
    [{'id': k, 'name': d['domain_name'], 'creation': d['timestamp'], 'index': d['index'], 'doc_type': d['doc_type']} for k, d in self._domains]

  def getAvailableProjectionAlgorithms(self):
    return [{'name': key} for key in self.projectionsAlg.keys()]

  # Returns a list of available seed crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableSeedCrawlers(self):
    # Initializes elastic search.
    self.es = es
    
    self._domains = get_available_domains(self.es)
    
    return \
    [{'id': k, 'name': d['domain_name'], 'creation': d['timestamp'], 'index': d['index'], 'doc_type': d['doc_type']} for k, d in self._domains.items()]

  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._activeCrawlerIndex = self._domains[crawlerId]['index']
    self._activeCrawlerId = crawlerId
    self._docType = self._domains[crawlerId]['doc_type']
    if not self._domains[crawlerId].get("mapping") is None:
      self._mapping = self._domains[crawlerId]["mapping"]
      
    self._filter = None

  def setActiveProjectionAlg(self, algId):
    self._activeProjectionAlg = algId

  def encode(self, url):
    return urllib2.quote(url).replace("/", "%2F")

  def createModel(self):

    data_dir = environ["DDT_HOME"] + "/data/"
    data_crawler  = data_dir + self._activeCrawlerIndex
    data_training = data_crawler + "/training_data/"
    data_negative = data_crawler + "/training_data/negative/"
    data_positive = data_crawler + "/training_data/positive/"

    if (not isdir(data_positive)):
      makedirs(data_positive)
    if (not isdir(data_negative)):
      makedirs(data_negative)

    pos_urls = [field['url'][0] for field in term_search(self._mapping['tag'], ['relevant'], ['url'], self._activeCrawlerIndex, 'page', self.es)]
    neg_urls = [field['url'][0] for field in term_search(self._mapping['tag'], ['irrelevant'], ['url'], self._activeCrawlerIndex, 'page', self.es)]
    
    pos_html = get_documents(pos_urls, 'url', [self._mapping["html"]], self._activeCrawlerIndex, self._docType)
    neg_html = get_documents(neg_urls, 'url', [self._mapping["html"]], self._activeCrawlerIndex, self._docType)

    seeds_file = data_crawler +"/seeds.txt"
    print "Seeds path ", seeds_file
    with open(seeds_file, 'w') as s:
      for url in pos_html:
        try:
          file_positive = data_positive + self.encode(url.encode('utf8'))
          print file_positive
          s.write(url.encode('utf8') + '\n')
          with open(file_positive, 'w') as f:
            f.write(pos_html[url][self._mapping['html']][0])

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
          f.write(neg_html[url]['html'][0])
      except IOError:
        _, exc_obj, tb = exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    
    models_dir = environ["DDT_HOME"] + "/vis/html/models/"
    crawlermodel_dir = models_dir + self._activeCrawlerIndex
    
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

    zip_filename = models_dir + self._activeCrawlerIndex + "_model.zip"
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
        modelzip.write(data_crawler +"/seeds.txt", self._activeCrawlerIndex + "_seeds.txt")

    chmod(zip_filename, 0o777)

    return "models/" + self._activeCrawlerIndex + "_model.zip"


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
  def getPagesSummaryCrawler(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False):
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
  def getPagesSummarySeedCrawler(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False):
    # If ts1 not specified, sets it to -Infinity.
    if opt_ts1 is None:
      now = time.localtime(0)
      opt_ts1 = float(time.mktime(now)) * 1000
    else:
      opt_ts1 = float(opt_ts1)

    # If ts2 not specified, sets it to now.
    if opt_ts2 is None:
      now = time.localtime()
      opt_ts2 = float(time.mktime(now)) * 1000
    else:
      opt_ts2 = float(opt_ts2)

    if opt_applyFilter:
      # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
      results = get_most_recent_documents(self._pagesCap, self._mapping, ["url", self._mapping["tag"]], 
                                          self._filter, self._activeCrawlerIndex, self._docType,  \
                                          self.es)
    else:
      results = \
      range(self._mapping["timestamp"], opt_ts1, opt_ts2, ['url',self._mapping['tag']], True, self._pagesCap, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)

    relevant = 0
    irrelevant = 0
    neutral = 0

    # TODO(Yamuna): Double check the return values for crawler
    for res in results:
        try:
          tags = res[self._mapping['tag']]
          if 'Relevant' in res[self._mapping['tag']]:
            relevant = relevant + 1
          elif 'Irrelevant' in res[self._mapping['tag']]:
            irrelevant = irrelevant + 1
          else:
            # Page has tags, but not Relevant or Irrelevant.
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
  def getTermsSummaryCrawler(self, opt_maxNumberOfTerms = 50):
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
  def getTermsSummarySeedCrawler(self, opt_maxNumberOfTerms = 50):
    s_fields = {
      "tag": "Positive",
      "index": self._activeCrawlerIndex,
      "doc_type": self._docType
    }
    pos_terms = [field['term'][0] for field in multifield_term_search(s_fields, ['term'], self._termsIndex, 'terms', self.es)]

    s_fields["tag"]="Negative"
    neg_terms = [field['term'][0] for field in multifield_term_search(s_fields, ['term'], self._termsIndex, 'terms', self.es)]
    

    pos_urls = [field['url'][0] for field in term_search(self._mapping['tag'], ['Relevant'], ['url'], self._activeCrawlerIndex, self._docType, self.es)]
    
    top_terms = []

    if self._filter is None:
      urls = []
      if len(pos_urls) > 0:
        # If positive urls are available search for more documents like them
        urls = [field['id'] for field in get_more_like_this(pos_urls, ['url'], self._pagesCapTerms,  self._activeCrawlerIndex, self._docType,  self.es)]
      
      if not urls:
        # If positive urls are not available then get the most recent documents
        urls = [field['id'] for field in get_most_recent_documents(self._pagesCapTerms, self._mapping, ['url'], self._filter, self._activeCrawlerIndex, self._docType, self.es)]

      if len(urls) > 1:
      
        tfidf_all = tfidf.tfidf(urls, self.w2v, self._mapping, self._activeCrawlerIndex, self._docType, self.es)
        extract_terms_all = extract_terms.extract_terms(tfidf_all)
      
        if pos_terms:
          [ranked_terms, scores] = extract_terms_all.results(pos_terms)
          top_terms = [ term for term in ranked_terms if (term not in neg_terms)]
          top_terms = top_terms[0:opt_maxNumberOfTerms]
        else:
          top_terms = extract_terms_all.getTopTerms(opt_maxNumberOfTerms)
    else:
      filter_terms = self._filter.split(' ')

      start=time.clock()

      top_terms = get_significant_terms(filter_terms, field=self._mapping["text"], fields=[self._mapping["text"]], termCount=opt_maxNumberOfTerms, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)

    if not top_terms:  
      return []

    pos_freq = {}
    if len(pos_urls) > 1:
      tfidf_pos = tfidf.tfidf(pos_urls, self.w2v, self._mapping, self._activeCrawlerIndex, self._docType, self.es)
      [_,corpus,ttfs_pos] = tfidf_pos.getTfArray()
      total_pos_tf = np.sum(ttfs_pos.toarray(), axis=0)
      total_pos = np.sum(total_pos_tf)
      pos_freq={}
      for key in top_terms:
        try:
          pos_freq[key] = (float(total_pos_tf[corpus.index(key)])/total_pos)
        except ValueError:
          pos_freq[key] = 0
    else:
      pos_freq = { key: 0 for key in top_terms }      

    neg_urls = [field['url'][0] for field in term_search(self._mapping['tag'], ['Irrelevant'], ['url'], self._activeCrawlerIndex, self._docType, self.es)]
    neg_freq = {}
    if len(neg_urls) > 1:
      tfidf_neg = tfidf.tfidf(neg_urls,  self.w2v, self._mapping, self._activeCrawlerIndex, self._docType,  self.es)
      [_,corpus,ttfs_neg] = tfidf_neg.getTfArray()
      total_neg_tf = np.sum(ttfs_neg.toarray(), axis=0)
      total_neg = np.sum(total_neg_tf)
      neg_freq={}
      for key in top_terms:
        try:
          neg_freq[key] = (float(total_neg_tf[corpus.index(key)])/total_neg)
        except ValueError:
          neg_freq[key] = 0
    else:
      neg_freq = { key: 0 for key in top_terms }      

    terms = []

    s_fields = {
      "term": "",
      "index": self._activeCrawlerIndex,
      "doc_type": self._docType,
    }

    results = []
    for term in top_terms:
      s_fields["term"] = term
      res = multifield_term_search(s_fields, ['tag'], self._termsIndex, 'terms', self.es)
      results.extend(res)

    tags = {result['id']: result['tag'][0] for result in results}    

    for term in top_terms:
      entry = [term, pos_freq[term], neg_freq[term], []]
      if tags and not tags.get(term) is None:
        entry[3] = tags[term].split(';')
      terms.append(entry)

    return terms


  # Sets limit to pages returned by @getPages.
  def setPagesCountCap(self, pagesCap):
    self._pagesCap = int(pagesCap)

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
  def getPages(self):

    start = time.clock()
    if self._filter is None:
      hits = get_most_recent_documents(opt_maxNumberOfPages=self._pagesCap, mapping=self._mapping, fields=["url", "x", "y", self._mapping["tag"], self._mapping["timestamp"], self._mapping["text"]], 
                                       es_index=self._activeCrawlerIndex,
                                       es_doc_type=self._docType,
                                       es=self.es)
    else:
      hits = get_most_recent_documents(self._pagesCap, self._mapping, ["url", "x", "y", self._mapping["tag"], self._mapping["timestamp"],self._mapping["text"]], 
                                       self._filter, self._activeCrawlerIndex, \
                                       self._docType, \
                                       self.es)


    last_downloaded_url_epoch = None
    docs = []

    for i, hit in enumerate(hits):
      if last_downloaded_url_epoch is None:
        if not hit.get(self._mapping['timestamp']) is None:
          last_downloaded_url_epoch = str(hit[self._mapping['timestamp']][0])

      doc = ["", 0, 0, [], "", ""]

      if not hit.get('url') is None:  
        doc[0] = hit.get('url')
      if not hit.get('x') is None:
        doc[1] = hit['x'][0]
      if not hit.get('y') is None:
        doc[2] = hit['y'][0]
      if not hit.get(self._mapping['tag']) is None:
        doc[3] = hit[self._mapping['tag']][0].split(';')
      if not hit.get('id') is None:
        doc[4] = hit['id']
      if not hit.get(self._mapping["text"]) is None:
        doc[5] = hit[self._mapping["text"]][0]

      docs.append(doc)
    
    if len(docs) > 1:
      # Prepares results: computes projection.
      # Update x, y for pages after projection is done.
      projectionData = self.projectPages(docs, self._activeProjectionAlg)

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

    else:
      return {'pages': []}

  # Boosts set of pages: crawler exploits outlinks for the given set of pages in active crawler.
  def boostPages(self, pages):
    # TODO(Yamuna): Issue boostPages on running crawler defined by active crawlerId.
    i = 0
    print 3 * '\n', 'boosted pages', str(pages), 3 * '\n'

  # Fetches snippets for a given term.
  def getTermSnippets(self, term):

    #tags = get_documents(term, 'term', ['tag'], self._activeCrawlerIndex, 'terms', self.es)


    s_fields = {
      "term": term,
      "index": self._activeCrawlerIndex,
      "doc_type": self._docType,
    }

    tags = multifield_term_search(s_fields, ['tag'], self._termsIndex, 'terms', self.es)
    
    tag = []
    if tags:
      tag = tags[0]['tag'][0].split(';')

    return {'term': term, 'tags': tag, 'context': get_context([term], self._activeCrawlerIndex, self._docType,  self.es)}

  # Adds tag to pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  def setPagesTag(self, pages, tag, applyTagFlag):

    entries = {}
    results = get_documents(pages, 'url', [self._mapping['tag']], self._activeCrawlerIndex, self._docType,  self.es)

    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to pages' + str(pages) + '\n\n'
      for page in pages:
        entry = {}
        if len(results) > 0 and not results.get(page) is None:
            if  not results[page].get(self._mapping['tag']) is None:
              entry[self._mapping['tag']] = results[page][self._mapping['tag']][0] +';'+tag
            else:
              entry[self._mapping['tag']] = tag
            entries[results[page]['id']] =  entry
    else:
      print '\n\nremoved tag ' + tag + ' from pages' + str(pages) + '\n\n'
      for page in pages:
        entry = {}
        if len(results) > 0 and not results.get(page) is None:
          if not results[page].get(self._mapping['tag']) is None:
            if tag in results[page][self._mapping['tag']]:
              tags = list(set(results[page][self._mapping['tag']][0].split(';')))
              tags.remove(tag)
              entry[self._mapping['tag']] = ';'.join(tags)
              entries[results[page]['id']] = entry

    if entries:
      update_try = 0
      while (update_try < 10):
        try:
          update_document(entries, self._activeCrawlerIndex, self._docType, self.es)
          break
        except:
          update_try = update_try + 1

    
  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.

    s_fields = {
      "term": "",
      "index": self._activeCrawlerIndex,
      "doc_type": self._docType,
    }

    tags = []
    for term in terms:
      s_fields["term"] = term
      res = multifield_term_search(s_fields, ['tag'], self._termsIndex, 'terms', self.es)
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
              "index": self._activeCrawlerIndex,
              "doc_type": self._docType
            }
            add_entries.append(entry)
          else:
            old_tag = results[term]
            if tag not in old_tag:
              entry = {
                "term" : term,
                "tag" : tag,
                "index": self._activeCrawlerIndex,
                "doc_type": self._docType
              }
              update_entries[term] = entry
        else:
          entry = {
            "term" : term,
            "tag" : tag,
            "index": self._activeCrawlerIndex,
            "doc_type": self._docType
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
                "index": self._activeCrawlerIndex,
                "doc_type": self._docType
              }
              update_entries[term] = entry

    if add_entries:
      add_document(add_entries, self._termsIndex, 'terms', self.es)
    
    if update_entries:
      update_document(update_entries, self._termsIndex, 'terms', self.es)

  # Add crawler
  def addCrawler(self, index_name):

    create_index(index_name, self.es)
    
    fields = index_name.lower().split(' ')
    index = '_'.join([item for item in fields if item not in ''])
    index_name = ' '.join([item for item in fields if item not in ''])
    entry = { "domain_name": index_name.title(),
              "index": index,
              "doc_type": "page",
              "timestamp": datetime.utcnow(),
            }

    load_config([entry])

    
  # Submits a web query for a list of terms, e.g. 'ebola disease'
  def queryWeb(self, terms, max_url_count = 100):
    # TODO(Yamuna): Issue query on the web: results are stored in elastic search, nothing returned
    # here.
    
    chdir(environ['DDT_HOME']+'/seeds_generator')
    
    with open('conf/queries.txt','w') as f:
      f.write(terms)

    comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar BingSearch -t " + str(max_url_count) + \
           " -i " + self._activeCrawlerIndex + \
           " -d " + self._docType + \
           " -s " + es_server

    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors
    
  # Applies a filter to crawler results, e.g. 'ebola disease'
  def applyFilter(self, terms):
    # The filter is just cached, and should be used in getPages (always) and getPagesSummary
    # (when the optional flag is set to True). Check those methods signatures.
    if terms:
      self._filter = terms
    else:
      self._filter = None


  # Projects pages.
  def projectPages(self, pages, projectionType='TSNE'):
    return self.projectionsAlg[projectionType](pages)
    
  # Projects pages with PCA
  def pca(self, pages):
    
    urls = [page[4] for page in pages]
    text = [page[5] for page in pages]
    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #[urls, data] = CrawlerModel.w2v.process(urls, self._mapping, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)
  
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

    #[urls, data] = CrawlerModel.w2v.process(urls, self._mapping, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)
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

    #[urls, data] = CrawlerModel.w2v.process(urls, self._mapping, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)
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

    [data, data_tf, data_ttf , corpus, urls] = getTermStatistics(urls, self.w2v, self._mapping, self._activeCrawlerIndex, self._docType, self.es)
    return [data.toarray(), data_tf, data_ttf, corpus, urls]

  @staticmethod
  def runPCASKLearn(X, pc_count = None):
    pca = PCA(n_components=pc_count)
    #pca.fit(X)
    #return [pca.explained_variance_ratio_.tolist(), pca.fit_transform(X).tolist()]
    return [None, pca.fit_transform(X).tolist()]

  @staticmethod
  def runTSNESKLearn(X, pc_count = None):
    tsne = TSNE(n_components=pc_count, random_state=0, metric='cosine')
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

