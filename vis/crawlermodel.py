import math
import time
from sklearn.decomposition import PCA
from random import random, randint



class CrawlerModel:
  def __init__(self):
    #TODO(yamuna): Instantiate Elastic Search client, and use the same instance for all queries.
    self._es = None



  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    # TODO(Yamuna): Query Elastic Search or other internal structure to return name, Id and time of
    # creation of available crawlers.
    return [ \
        {'id': 0, 'name': 'Ebola', 'creation': 1431544719},
        {'id': 1, 'name': 'Gun control', 'creation': 1430040719},
    ]



  # Returns a list of available seed crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableSeedCrawlers(self):
    # TODO(Yamuna): Query Elastic Search or other internal structure to return name, Id and time of
    # creation of available crawlers.
    return [ \
        {'id': 0, 'name': 'Ebola', 'creation': 1431544719},
        {'id': 1, 'name': 'Gun control', 'creation': 1430040719},
    ]



  # Returns number of pages downloaded between ts1 and ts2 for crawler with Id crawlerId.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # Returns dictionary in the format:
  # {
  #   'positive': {'explored': numExploredPages, 'exploited': numExploitedPages},
  #   'negative': {'explored': numExploredPages, 'exploited': numExploitedPages},
  # }
  def getPagesSummary(self, crawlerId, opt_ts1 = None, opt_ts2 = None):
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
    print opt_ts1

    inc = opt_ts2 - opt_ts1
    explored = int(opt_ts1 / 10E6 + inc)
    exploited = int(opt_ts1 / 10E8 + inc / 2)
    neutral = int(opt_ts1 / 10E8 + inc / 2)
    return { \
      'positive': {'explored': explored, 'exploited': exploited, 'neutral': neutral},
      'negative': {'explored': explored / 5, 'exploited': exploited / 5, 'neutral':  neutral / 5},
    }



  # Returns number of terms present in positive and negative pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   ...
  # ]
  def getTermsSummary(self, crawlerId):
    # TODO(Yamuna): Query Elastic Search (schema crawlerId) for terms in positive/negative
    # downloaded pages.
    return 9 * [ \
      ['Word', randint(1, 100), randint(1, 100)],
      ['Disease', randint(1, 100), randint(1, 100)],
      ['Control', randint(1, 100), randint(1, 100)],
      ['Symptoms', randint(1, 100), randint(1, 100)],
      ['Epidemy', 100, 100],
    ]



  # Returns pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
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
    return { \
      'positive': {
        'explored': 1 * [['usatoday.com', random(), random(), 'tag1;tag2'], ['globo.com', random(), random()], ['cnn.com', random(), random()], ['news.google.com', random(), random()],],
        'exploited': 1 * [['bbc.com', random(), random()], ['wired.com', random(), random()],],
      }, 
      'negative': {
        'explored': 1 * [['nydailynews.com', random(), random()], ['cnet.com', random(), random()], ['news.yahoo.com', random(), random()],],
        'exploited': 1 * [['nbcnews.com', random(), random()],],
      },
    }



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
      print 'applied tag ', tag, 'to pages', str(pages)
    else:
      print 'removed tag ', tag, 'to page', str(pages)



  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, crawlerId, term, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.
    if applyTagFlag:
      print 'applied tag ', tag, 'to term', str(terms)
    else:
      print 'removed tag ', tag, 'to term', str(terms)




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
  def runPCASKLearn(X, pc_count = None):
    pca = PCA(n_components=pc_count)
    pca.fit(X)
    return [pca.explained_variance_ratio_.tolist(), pca.transform(X).tolist()]



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



  def _onQueryDone(self, x):
    print '\n\n\n query is done\n\n'
    self.queryDone = True



  def getQueryResults(self):
    self.urls = list(self._crawlerModel.urls_set)

    # TODO When downloading in parallel, it should wait for pages content to be ready for tf-idf
    # computation.
    # Computes PCA with tf-idf vectors for urls.
    print len(self.urls)
    print self.urls

    # Gets tf-idf for terms.
    [self.urls, corpus, data] = self._crawlerModel.term_tfidf()
    print '\n\n\ntfidf'
    print '\n\n\n', data

    print data

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
