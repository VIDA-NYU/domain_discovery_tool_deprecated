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

from os import chdir, listdir, environ
from os.path import isfile, join, exists


from pyelasticsearch import ElasticSearch
from elasticsearch import Elasticsearch

from seeds_generator.download import download, decode
from seeds_generator.concat_nltk import get_bag_of_words
from elastic.get_config import get_available_domains
from elastic.search_documents import get_context, term_search, search, range
from elastic.add_documents import add_document, update_document, refresh
from elastic.get_mtermvectors import getTermStatistics
from elastic.get_documents import get_most_recent_documents, get_documents, get_all_ids, get_more_like_this
from elastic.aggregations import get_significant_terms
from elastic.create_index import create_index
from elastic.load_config import load_config
from elastic.create_config_index import create_config_index
from elastic.config import es, es_elastic, es_doc_type

from ranking import tfidf, rank, extract_terms, word2vec



class CrawlerModel:
  def __init__(self):
    self.es = None
    self.es_elastic = None
    self._activeCrawlerIndex = None
    self._activeProjectionAlg = None
    self._docType = None
    self._filter = None
    self._pagesCap = int(10E2)
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



  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    # Initializes elastic search.
    self.es = es
    self.es_elastic = es_elastic
    self._docType = es_doc_type

    domains = get_available_domains(self.es)
    return \
    [{'id': d['index'], 'name': d['domain_name'], 'creation': d['timestamp']} for d in domains]

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
    self.es_elastic = es_elastic
    self._docType = es_doc_type

    domains = get_available_domains(self.es)
    return \
    [{'id': d['index'], 'name': d['domain_name'], 'creation': d['timestamp']} for d in domains]


  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._activeCrawlerIndex = crawlerId
    self._filter = None

  def setActiveProjectionAlg(self, algId):
    self._activeProjectionAlg = algId

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
      opt_ts1 = float(time.mktime(now))
    else:
      opt_ts1 = float(opt_ts1)

    # If ts2 not specified, sets it to now.
    if opt_ts2 is None:
      now = time.localtime()
      opt_ts2 = float(time.mktime(now))
    else:
      opt_ts2 = float(opt_ts2)

    if opt_applyFilter:
      # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
      results = get_most_recent_documents(self._pagesCap, ["url", "tag"], 
                                          self._filter, self._activeCrawlerIndex, self._docType, \
                                          self.es)
    else:
      results = \
      range('retrieved',opt_ts1, opt_ts2, ['url','tag'], True, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)

    relevant = 0
    irrelevant = 0
    neutral = 0

    # TODO(Yamuna): Double check the return values for crawler
    for res in results:
        try:
          tags = res['tag']
          if 'Relevant' in res['tag']:
            relevant = relevant + 1
          elif 'Irrelevant' in res['tag']:
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

    pos_terms = term_search('tag', ['Positive'], self._activeCrawlerIndex, 'terms', self.es)
    neg_terms = term_search('tag', ['Negative'], self._activeCrawlerIndex, 'terms', self.es)
    
    terms = []
    pos_urls = term_search('tag', ['Relevant'], self._activeCrawlerIndex, self._docType, self.es)

    top_terms = []

    if self._filter is None:
      urls = []
      if len(pos_urls) > 0:
        urls = get_more_like_this(pos_urls, 500,  self._activeCrawlerIndex, self._docType, self.es)
      else:
        urls = get_all_ids(1000, self._activeCrawlerIndex, self._docType, self.es)
            
      if len(urls) > 1:
      
        tfidf_all = tfidf.tfidf(urls, self._activeCrawlerIndex, self._docType, self.es_elastic)
        extract_terms_all = extract_terms.extract_terms(tfidf_all)
      
        if pos_terms:
          [ranked_terms, scores] = extract_terms_all.results(pos_terms)
          top_terms = [ term for term in ranked_terms if (term not in neg_terms)]
          top_terms = top_terms[0:opt_maxNumberOfTerms]
        else:
          top_terms = extract_terms_all.getTopTerms(opt_maxNumberOfTerms)
    else:
      filter_terms = self._filter.split(' ')
      top_terms = get_significant_terms(filter_terms, termCount=opt_maxNumberOfTerms, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es)

    if not top_terms:  
      return []

    tags = get_documents(top_terms, 'term', ['tag'], self._activeCrawlerIndex, 'terms', self.es)

    pos_freq = {}
    if len(pos_urls) > 1:
      tfidf_pos = tfidf.tfidf(pos_urls, self._activeCrawlerIndex, self._docType, self.es_elastic)
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

    neg_urls = term_search('tag', ['Irrelevant'], self._activeCrawlerIndex, self._docType, self.es)
    neg_freq = {}
    if len(neg_urls) > 1:
      tfidf_neg = tfidf.tfidf(neg_urls, self._activeCrawlerIndex, self._docType, self.es_elastic)
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

    for term in top_terms:
      entry = [term, pos_freq[term], neg_freq[term], []]
      if not tags.get(term) is None:
        entry[3] = tags[term]['tag'].split(';')
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
    
    if self._filter is None:
      hits = get_most_recent_documents(fields=["url", "x", "y", "tag", "retrieved"], 
                                       es_index=self._activeCrawlerIndex,
                                       es_doc_type=self._docType,
                                       es=self.es)
    else:
      hits = get_most_recent_documents(self._pagesCap, ["url", "x", "y", "tag", "retrieved"], 
                                       self._filter, self._activeCrawlerIndex, self._docType, \
                                       self.es)
    
    last_downloaded_url_epoch = None
    docs = []
    for i, hit in enumerate(hits):
      if last_downloaded_url_epoch is None:
        if not hit.get('retrieved') is None:
          last_downloaded_url_epoch = hit['retrieved'][0]

      doc = ["", 0, 0, []]
      if not hit.get('url') is None:
        doc[0] = hit['url'][0]
      if not hit.get('x') is None:
        doc[1] = hit['x'][0]
      if not hit.get('y') is None:
        doc[2] = hit['y'][0]
      if not hit.get('tag') is None:
        doc[3] = hit['tag'][0].split(';')

      docs.append(doc)                                                                                                                     

    if len(docs) > 1:
      # Prepares results: computes projection.
      # Update x, y for pages after projection is done.

      projectionData = self.projectPages(docs, self._activeProjectionAlg)

      format = '%Y-%m-%dT%H:%M:%S.%f'
      if '+' in last_downloaded_url_epoch:
        format = '%Y-%m-%dT%H:%M:%S.%f+0000'

      last_download_epoch = CrawlerModel.convert_to_epoch(datetime.strptime(last_downloaded_url_epoch, format))

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

    tags = get_documents(term, 'term', ['tag'], self._activeCrawlerIndex, 'terms', self.es)
    tag = []
    if tags:
      tag = tags[term]['tag'].split(';')

    return {'term': term, 'tags': tag, 'context': get_context([term], self._activeCrawlerIndex, self._docType, self.es)}

  # Adds tag to pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  def setPagesTag(self, pages, tag, applyTagFlag):

    entries = []
    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to pages' + str(pages) + '\n\n'
      results = get_documents(pages, 'url', ['tag'], self._activeCrawlerIndex, self._docType, self.es)
      for page in pages:
        entry = {}
        entry['url'] = page
        if len(results) > 0:
          if not results.get(page) is None:
            if results.get(page)['tag']:
              entry['tag'] = results.get(page)['tag'] +';'+tag
            else:
              entry['tag'] = tag
          else:
            entry['tag'] = tag
        else:
          entry['tag'] = tag
        entries.append(entry)
    else:
      results = get_documents(pages, 'url', ['tag'], self._activeCrawlerIndex, self._docType, self.es)
      print '\n\nremoved tag ' + tag + ' from pages' + str(pages) + '\n\n'
      for page in pages:
        entry = {}
        if len(results) > 0 and not results.get(page) is None:
          if tag in results.get(page)['tag']:
            entry['url'] = page
            tags = list(set(results.get(page)['tag'].split(';')))
            tags.remove(tag)
            entry['tag'] = ';'.join(tags)
            entries.append(entry)

    if entries:
      update_try = 0
      while (update_try < 10):
        try:
          update_document(entries, 'url', self._activeCrawlerIndex, self._docType, self.es)
          break
        except BulkError:
          update_try = update_try + 1
    
    refresh(self._activeCrawlerIndex, self.es)

  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.

    results = get_documents(terms, 'term', ['tag'], self._activeCrawlerIndex, 'terms', self.es)
    
    add_entries = []
    update_entries = []

    if applyTagFlag:
      for term in terms:
        if len(results) > 0:
          if results.get(term) is None:
            entry = {
              "term" : term,
              "tag" : tag
            }
            add_entries.append(entry)
          else:
            old_tag = results[term]['tag']
            if tag not in old_tag:
              entry = {
                "term" : term,
                "tag" : tag
              }
              update_entries.append(entry)
        else:
          entry = {
            "term" : term,
            "tag" : tag
          }
          add_entries.append(entry)
    else:
      for term in terms:
        if len(results) > 0:
          if not results.get(term) is None:
            if tag in results[term]['tag']:
              entry = {
                "term" : term,
                "tag" : ""
              }
              update_entries.append(entry)

    if add_entries:
      add_document(add_entries, self._activeCrawlerIndex, 'terms', self.es)
    
    if update_entries:
      update_document(update_entries, 'term', self._activeCrawlerIndex, 'terms', self.es)

  # Add crawler
  def addCrawler(self, index_name):

    create_index(index_name, self.es_elastic)
    
    fields = index_name.lower().split(' ')
    index = '_'.join([item for item in fields if item not in ''])
    index_name = ' '.join([item for item in fields if item not in ''])
    entry = { "domain_name": index_name.title(),
              "index": index
            }

    load_config([entry])

    
  # Submits a web query for a list of terms, e.g. 'ebola disease'
  def queryWeb(self, terms, max_url_count = 500):
    # TODO(Yamuna): Issue query on the web: results are stored in elastic search, nothing returned
    # here.
    
    chdir(environ['DDT_HOME']+'/seeds_generator')
    
    with open('conf/queries.txt','w') as f:
      f.write(terms)

    comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar BingSearch -t " + str(max_url_count) + \
           " -i " + self._activeCrawlerIndex + \
           " -d " + self._docType
           #" -s " + environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in environ else 'http://localhost:9200'

    p=Popen(comm, shell=True, stderr=PIPE)
    output, errors = p.communicate()
    print output
    print errors
    
    #download("results.txt", self._activeCrawlerIndex, self._docType, environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in environ else 'http://localhost:9200')

  # Applies a filter to crawler results, e.g. 'ebola disease'
  def applyFilter(self, terms):
    # The filter is just cached, and should be used in getPages (always) and getPagesSummary
    # (when the optional flag is set to True). Check those methods signatures.
    if terms:
      self._filter = terms


  # Projects pages.
  def projectPages(self, pages, projectionType='TSNE'):
    return self.projectionsAlg[projectionType](pages)
    
  # Projects pages with PCA
  def pca(self, pages):
    
    urls = [page[0] for page in pages]
    #[data,_,_,_,urls] = self.term_tfidf(urls)

    w2v = word2vec.word2vec(urls, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es_elastic)
    [urls, data] = w2v.get_word2vec()

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    pca_count = 2
    pcadata = CrawlerModel.runPCASKLearn(data, pca_count)

    try:
      results = []
      i = 0
      for page in pages:
        if page[0] in urls:
          page[1] = pcadata[1][i][0]
          page[2] = pcadata[1][i][1]
          i = i + 1
          results.append(page)
    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i
    return pages

  # Projects pages with TSNE
  def tsne(self, pages):
    
    urls = [page[0] for page in pages]
    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    w2v = word2vec.word2vec(urls, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es_elastic)
    [urls, data] = w2v.get_word2vec()
    
    tsne_count = 2
    tsnedata = CrawlerModel.runTSNESKLearn(data, tsne_count)

    try:
      results = []
      i = 0
      for page in pages:
        if page[0] in urls:
          page[1] = tsnedata[1][i][0]
          page[2] = tsnedata[1][i][1]
          i = i + 1
          results.append(page)
    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i
    return pages

  # Projects pages with KMeans
  def kmeans(self, pages):
    
    urls = [page[0] for page in pages]

    #[data,_,_,_,urls] = self.term_tfidf(urls)

    #Convert to binary
    #data = data.astype(bool)
    #data = data.astype(int)

    w2v = word2vec.word2vec(urls, es_index=self._activeCrawlerIndex, es_doc_type=self._docType, es=self.es_elastic)
    [urls, data] = w2v.get_word2vec()

    k = 5
    kmeansdata = CrawlerModel.runKMeansSKLearn(data, k)
    
    try:
      results = []
      i = 0
      for page in pages:
        if page[0] in urls:
          page[1] = kmeansdata[1][i][0]
          page[2] = kmeansdata[1][i][1]
          i = i + 1
          results.append(page)
    except IndexError:
      print 'INDEX OUT OF BOUNDS ',i
    return pages

  def term_tfidf(self, urls):

    [data, data_tf, data_ttf , corpus, urls] = getTermStatistics(urls, self._activeCrawlerIndex, self._docType, self.es_elastic)
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

