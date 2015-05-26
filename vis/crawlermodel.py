import math
import time
import os
from sklearn.decomposition import PCA
from random import random, randint
from pprint import pprint
from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from os import chdir, listdir, environ
from os.path import isfile, join, exists
import shutil
import sys

from seeds_generator.download import download, decode
from seeds_generator.concat_nltk import get_bag_of_words

from pyelasticsearch import ElasticSearch
from elastic.get_config import get_available_domains
from elastic.search_documents import get_context, term_search, search, range
from elastic.add_documents import update_document
from elastic.get_mtermvectors import getTermStatistics
from ranking import tfidf, rank, extract_terms

class CrawlerModel:
  def __init__(self):
    #TODO(yamuna): Instantiate Elastic Search client, and use the same instance for all queries.
    self.es = ElasticSearch(os.environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in os.environ else 'http://localhost:9200')
    self._activeCrawlerIndex = None
    self._filter = None



  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    # TODO(Yamuna): Query Elastic Search or other internal structure to return name, Id and time of
    # creation of available crawlers.
    domains = get_available_domains(self.es)
    return [{'id': d['index'], 'name', d['domain_name'], 'creation': d['timestamp']} for d in domains]



  # Returns a list of available seed crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableSeedCrawlers(self):
    # TODO(Yamuna): Query Elastic Search or other internal structure to return name, Id and time of
    # creation of available crawlers.
    domains = get_available_domains(self.es)
    return [{'id': d['index'], 'name', d['domain_name'], 'creation': d['timestamp']} for d in domains]


  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._activeCrawlerIndex = crawlerId



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

    # TODO(Yamuna): Query Elastic Search (schema crawlerId) for number of downloaded pages between
    # given Unix epochs.
    print 'from ', opt_ts1
    print 'to ', opt_ts2
    print 'index ', self._activeCrawlerIndex

    results = range('retrieved',opt_ts1, opt_ts2, ['url','tag'], True, self._activeCrawlerIndex, es=self.es )

    positive = 0
    negative = 0
    neutral = 0

    # TODO(Yamuna): Double check the return values for crawler
    for res in results:
      try:
        if 'Positive' in res['tag']:
          positive = positive + 1
        if 'Negative' in res['tag']:
          negative = negative + 1
      except KeyError:
        neutral = neutral + 1

    return { \
      'Positive': positive,
      'Negative': negative,
      'Neutral': neutral
    }



  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # Returns dictionary in the format:
  # {
  #   'positive': {'explored': [[url1, x, y, tags], ...], 'exploited': [[url1, x, y], ...]},
  #   'negative': {'explored': [[url1, x, y, tags], ...], 'exploited': [[url1, x, y], ...]},
  # }
  def getPages(self, crawlerId, opt_ts1 = None, opt_ts2 = None):
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

    # TODO(Yamuna): Query Elastic Search (schema crawlerId) for positive/negative pages between ts1
    # and ts2.
    # TODO(Yamuna): maybe positive/explored/exploited etc can be tags.

    results = range('retrieved',opt_ts1, opt_ts2, ['url','tag'], true, self.domains[crawlerid]['index'], es=self.es )

    positive = {}
    negative = {}

    for res in results:
      try:
        if 'positive' in res['tag']:
          positive[res['url']] = [res['tag']]
        if 'negative' in res['tag']:
          negative[res['url']] = [res['tag']]
      except keyerror:
        pass

    pc_count = 2        
    if len(pos.keys()) > 0:
      [pos_urls, pos_corpus, pos_data] = self.term_tfidf(positive.keys())
      pos_pcadata = crawlermodeladapter.runpcasklearn(pos_data, pc_count)
      print pos_pcadata

    if len(pos.keys()) > 0:
      [neg_urls, neg_corpus, neg_data] = self.term_tfidf(negative.keys())
      pos_pcadata = crawlermodeladapter.runpcasklearn(neg_data, pc_count)
      print neg_pcadata

    return json.dumps([postive, negative]) 

  # Boosts set of pages: crawler exploits outlinks for the given set of pages in crawlerId.
  def boostPages(self, crawlerId, pages):
    # TODO(Yamuna): Issue boostPages on running crawler defined by crawlerId.
    i = 0
    print 3 * '\n', 'boosted pages', str(pages), 3 * '\n'



  # Fetches snippets for a given term.
  def getTermSnippets(self, crawlerId, term):
    # TODO(Yamuna): Fetch snippets for given term on running crawler defined by crawlerId.
    snippets = 15 * [3 * 'nho' + ' ' + term + ' ' + 10 * 'la']
    return {'term': term, 'label': 'positive', 'context': snippets}



  # Adds tag to pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  def setPagesTag(self, crawlerId, pages, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.
    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to pages' + str(pages) + '\n\n'
    else:
      print '\n\nremoved tag ' + tag + ' from pages' + str(pages) + '\n\n'



  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, crawlerId, terms, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.
    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to terms' + str(terms) + '\n\n'
    else:
      print '\n\nremoved tag ' + tag + ' from terms' + str(terms) + '\n\n'




  # TODO(Yamuna): from here on we need to discuss the best strategy.
  ##########
  ##########
  ##########
  ##########
  ##########
  ##########
  ##########
  ##########






  def query( \
  self, queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms):
    # Issues query.
    self.issueQuery( \
    queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms)

    # Waits for query completion when using parallel execution for queries.
    if self._useParallelQueries:
      # Hangs until query is done.
      while not self.isQueryDone():
        i = 0
    return self.getQueryResults()


  @staticmethod
  def extractListParam(param, opt_char = None):
    divider = opt_char if opt_char != None else '|'
    return param.split(divider) if len(param) > 0 else []



  def query( \
  self, queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms):
    # Issues query.
    self.issueQuery( \
    queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms)

    # Waits for query completion when using parallel execution for queries.
    if self._useParallelQueries:
      # Hangs until query is done.
      while not self.isQueryDone():
        i = 0
    return self.getQueryResults()



  def isQueryDone(self):
    return self.queryDone



  def getQueryResults(self):
    self.urls = list(self._crawlerModel.urls_set)

    # TODO When downloading in parallel, it should wait for pages content to be ready for tf-idf
    # computation.
    # Computes PCA with tf-idf vectors for urls.
    print len(self.urls)
    print self.urls

    # Gets tf-idf for terms.
    [self.urls, corpus, data] = self.term_tfidf()

    pc_count = 2
    pcaData = CrawlerModelAdapter.runPCASKLearn(data, pc_count)

    # TODO Read thumbnails.
    positiveUrls = self._crawlerModel.positive_urls_set
    negativeUrls = self._crawlerModel.negative_urls_set
    self.urlsInfo = []
    for url in self.urls:
      # TODO Get thumbnail for url.
      thumbnail = None
      urlInfo = {'url': url, 'thumbnail': thumbnail}
      self.urlsInfo.append(urlInfo)
      if url in positiveUrls:
        urlInfo['label'] = 'positive'
      elif url in negativeUrls:
        urlInfo['label'] = 'negative'

    return {'urls': self.urlsInfo, 'pcaData': pcaData}



  def issueQuery( \
  self, queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms):
    # Always performs reranking when submitting a query to avoid losing current labels.
    if len(positivePages) > 0 or len(negativePages) > 0:
      positive_pages_list = CrawlerModelAdapter.extractListParam(positivePages)
      negative_pages_list = CrawlerModelAdapter.extractListParam(negativePages)
      self._crawlerModel.submit_selected_urls(positive_pages_list, negative_pages_list)

    # Always updates labels for terms when submitting a query to avoid losing current labels.
    if len(positiveTerms) > 0 or len(negativeTerms) > 0:
      self._updateTermsLabels(positiveTerms, negativeTerms, neutralTerms)

    # Performs query.
    query_term_list = CrawlerModelAdapter.extractListParam(queryTerms, ' ')
    onFinishedCb = (lambda x:self._onQueryDone(x)) if self._useParallelQueries else None
    self.queryDone = False
    # Performs query.
    self._crawlerModel.submit_query_terms(query_term_list, self._MAX_URL_COUNT, \
    parallel_cb = onFinishedCb, cached = self._useCachedQueries)

    print '\n\n\n', '*' * 80
    print 'issued query_term_list', query_term_list
    print '*' * 80, '\n\n\n'




  def doRanking(self, positivePages, negativePages):
    positive_pages_list = CrawlerModelAdapter.extractListParam(positivePages)
    negative_pages_list = CrawlerModelAdapter.extractListParam(negativePages)

#    print '\n\n\n', '*' * 80
#    print 'positive_pages_list', positive_pages_list
#    print 'negative_pages_list', negative_pages_list

    rank = self._crawlerModel.submit_selected_urls(positive_pages_list, negative_pages_list)
    print '\n\n\n', '*' * 80
#    print 'positive_pages_list', positive_pages_list
#    print 'negative_pages_list', negative_pages_list
    print rank
    print '\n\n\n', '*' * 80
    # TODO remove test after Yamuna fixes scores computation.
    ranked_urls = rank[0]
    scores = rank[1]
    scores = [0.5 if math.isnan(score) else score for score in scores]
    return {'ranked_urls': ranked_urls, 'scores': scores}



  def _updateTermsLabels(self, positiveTerms, negativeTerms, neutralTerms):
    positive_terms_list = CrawlerModelAdapter.extractListParam(positiveTerms)
    negative_terms_list = CrawlerModelAdapter.extractListParam(negativeTerms)
    neutral_terms_list = CrawlerModelAdapter.extractListParam(neutralTerms)

    self.positive_terms_set = self.positive_terms_set.union(set(positive_terms_list))
    self.negative_terms_set = self.negative_terms_set.union(set(negative_terms_list))

    for neutral_term in neutral_terms_list:
      self.positive_terms_set.discard(neutral_term)
      self.negative_terms_set.discard(neutral_term)

    # Extracts terms and loads their snippets.
    self._crawlerModel.submit_selected_urls([], [])
    self._crawlerModel.submit_selected_terms( \
    list(self.positive_terms_set), list(self.negative_terms_set))



  def extractTerms(self, positiveTerms, negativeTerms, neutralTerms):
    self._updateTermsLabels(positiveTerms, negativeTerms, neutralTerms)

    # Extracts terms and loads their snippets.
    terms = self._crawlerModel.extract_terms(self._MAX_EXTRACTED_TERMS_COUNT)

    new_terms_and_context = {term: self._crawlerModel.term_context([term]) for term in terms}

    # Appends to existing terms/context.
    for term, context in new_terms_and_context.iteritems():
      self.terms_and_context[term] = {'term': term, 'context': context, 'label': None}
      if term in self.positive_terms_set:
        self.terms_and_context[term]['label'] = 'positive'
      if term in self.negative_terms_set:
        self.terms_and_context[term]['label'] = 'negative'

    return self.terms_and_context.values()

    def submit_query_terms(self, term_list, max_url_count = 15, parallel_cb = None, cached=True):
    #Perform queries to Search Engine APIs
    #This function only operates when there is no information associated with the terms,
    #usually before running extract_terms()
    #
    #Args:
    #   term_list: list of search terms that are submited by user
    #Returns:
    #   urls: list of urls that are returned by Search Engine

        print '\n\nsubmit_query_terms\n\n'

        chdir(self.memex_home + '/seed_crawler/seeds_generator')
        
        query = ' '.join(term_list)
        with open('conf/queries.txt','w') as f:
            f.write(query)
            
        if not cached:
            comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar BingSearch -t " + str(max_url_count)
            p=Popen(comm, shell=True, stdout=PIPE)
            output, errors = p.communicate()
            print output
            print errors

        
            call(["rm", "-rf", "html"])
            call(["mkdir", "-p", "html"])
            call(["rm", "-rf", "thumbnails"])
            call(["mkdir", "-p", "thumbnails"])
        
            #if sys.platform in ['darwin', 'linux2']:
            if sys.platform in ['darwin']:
                download("results.txt")
            else:
                download("results.txt", True, parallel_cb)

            if exists(self.memex_home + "/seed_crawler/ranking/exclude.txt"):
                call(["rm", self.memex_home + "/seed_crawler/ranking/exclude.txt"])

            with open("results.txt",'r') as f:
                urls = [self.validate_url(line.strip()) for line in f.readlines()]
        else:
            urls = search('text', term_list)[0:max_url_count]

        for url in urls:
            self.urls_set.add(url)

        self.tfidf = tfidf.tfidf(list(self.urls_set))

        return urls #Results from Search Engine
        
    
    def submit_selected_urls(self, positive, negative):
    #Perform ranking and diversifing on all urls with regard to the positive urls
    #
    #Args:
    #   labeled_urls: a list of pair <url, label>. Label 1 means positive and 0 means negative.
    #Returns:
    #   urls: list of urls with ranking scores

        # Test new positive and negative examples with exisitng classifier
        # If accuracy above threshold classify pages
        # Ranking 
        # Diversification
        
        print '\n\nsubmit_selected_urls\n\n'

        entries = []
        for pos_url in positive:
            entry = {
                'url': pos_url,
                'relevance': 1
            }
            entries.append(entry)
            
        for neg_url in negative:
            entry = {
                'url': pos_url,
                'relevance': 0
            }
            entries.append(entry)

        if len(entries) > 0:
            update_document(entries)

        other = []
        
        for url in positive:
            if url in self.urls_set:
                self.positive_urls_set.add(url)
                self.negative_urls_set.discard(url)

        for url in negative:
            if url in self.urls_set:
                self.negative_urls_set.add(url)
                self.positive_urls_set.discard(url)
                
        for url in self.urls_set:
            if (len(self.negative_urls_set) == 0) or (url not in self.negative_urls_set):
                if url not in self.positive_urls_set:
                    other.append(url)

        chdir(self.memex_home + '/seed_crawler/ranking')
        ranker = rank.rank()
        
        [ranked_urls,scores] = ranker.results(self.tfidf,self.positive_urls_set, other)
        return [ranked_urls, scores] # classified, ranked, diversified 

    def extract_terms(self, count):
    #Extract salient terms from positive urls
    #
    #Returns:        
    #   terms: list of extracted salient terms and their ranking scores
        
        print '\n\nextract_terms\n\n'

        chdir(self.memex_home + '/seed_crawler/ranking')
        if exists("selected_terms.txt"):
            call(["rm", "selected_terms.txt"])
        if exists("exclude.txt"):
            call(["rm", "exclude.txt"])

        extract = extract_terms.extract_terms(self.tfidf)
        return extract.getTopTerms(count)

    #def term_frequency(self):
     #   all_docs = get_bag_of_words(list(self.urls_set))
      #  return tfidf.tfidf(all_docs).getTfArray()

    def term_tfidf(self):
        urls = list(self.urls_set)
        [data, corpus] = getTermStatistics(urls)
        #all_docs = get_bag_of_words(list(self.urls_set))
        #return tfidf.tfidf(all_docs).getTfidfArray()
        return [urls, corpus, data.toarray()]

    def submit_selected_terms(self, positive, negative):
    #Rerank the terms based on the labeled terms
    #
    #Args:
    #   labeled_terms: list of pair of term and label: <term, label>. Label 1 means postive, 0 means negative.
    #Returns:
    #   terms: list of newly ranked terms and their ranking scores

        print '\n\nsubmit_selected_terms\n\n'

        terms = []
        chdir(self.memex_home+'/seed_crawler/ranking')
        
        past_yes_terms = []
        if exists("selected_terms.txt"):
            with open('selected_terms.txt','r') as f:
                past_yes_terms = [line.strip() for line in f.readlines()]

        with open('selected_terms.txt','w+') as f:
            for word in past_yes_terms:
                f.write(word+'\n')
            for choice in positive :
                if choice not in past_yes_terms:
                    f.write(choice+'\n')

        past_no_terms = []
        if exists("exclude.txt"):
            with open('exclude.txt','r') as f:
                past_no_terms = [line.strip() for line in f.readlines()]

        with open('exclude.txt','w+') as f:
            for word in past_no_terms:
                f.write(word+'\n')
            for choice in negative :
                if choice not in past_no_terms:
                    f.write(choice+'\n')

        extract = extract_terms.extract_terms(self.tfidf)
        [ranked_terms, scores] = extract.results(past_yes_terms + positive)

        ranked_terms = [ term for term in ranked_terms if (term not in past_no_terms) and (term not in negative)]
                
        return ranked_terms # ranked

    def term_context(self, terms):
        return get_context(terms)

    def validate_url(self, url):
        s = url[:4]
        if s == "http":
            return url
        else:
            url = "http://" + url
        return url
