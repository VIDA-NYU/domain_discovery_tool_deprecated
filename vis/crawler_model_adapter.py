import math
#FIXME(yamuna): Import crawler model.
#from crawler_model import *
from crawlermodel import *

class CrawlerModelAdapter:
  def __init__(self):
    #TODO(yamuna): Instantiate crawler model.
    self._crawlerModel = CrawlerModel()
    self._activeCrawlerId = None
    self._currentTs = None



  # Extracts boolean parameter.
  @staticmethod
  def extractBooleanParam(param):
    return param == 'true'



  # Extracts list of parameters: array is encoded as a long string with a delimiter.
  @staticmethod
  def extractListParam(param, opt_char = None):
    delimiter = opt_char if opt_char != None else '|'
    return param.split(delimiter) if len(param) > 0 else []



  # Returns a list of available crawlers sorted by name, creation date, in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    crawlers = self._crawlerModel.getAvailableCrawlers()
    return sorted(crawlers, key = lambda c: (c['name'], c['creation']))



  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._activeCrawlerId = crawlerId
    # TODO(cesar): Resets data structures holding data about active crawler.
    print '\n\n', 'Active crawler:', self._activeCrawlerId, '\n\n'



  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # Returns dictionary in the format:
  # {
  #   'positive': {'explored': numExploredPages, 'exploited': numExploitedPages},
  #   'negative': {'explored': numExploredPages, 'exploited': numExploitedPages},
  # }
  def getPagesSummary(self, opt_ts1 = None, opt_ts2 = None):
    return self._crawlerModel.getPagesSummary(self._activeCrawlerId, opt_ts1, opt_ts2)



  # Returns number of terms present in positive and negative pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   ...
  # ]
  def getTermsSummary(self):
    return self._crawlerModel.getTermsSummary(self._activeCrawlerId)



  # Returns pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # Returns dictionary in the format:
  # {
  #   'positive': {'explored': [[url1, x, y], ...], 'exploited': [[url1, x, y], ...]},
  #   'negative': {'explored': [[url1, x, y], ...], 'exploited': [[url1, x, y], ...]},
  # }
  def getPages(self, opt_ts1 = None, opt_ts2 = None):
    return self._crawlerModel.getPages(self._activeCrawlerId, opt_ts1, opt_ts2)



  # Boosts set of pages: crawler exploits outlinks for the given set of pages.
  def boostPages(self, pages):
    pages = CrawlerModelAdapter.extractListParam(pages)
    return self._crawlerModel.boostPages(self._activeCrawlerId, pages)



  # Fetches snippets for a given term.
  def getTermSnippets(self, term):
    return self._crawlerModel.getTermSnippets(self._activeCrawlerId, term)



  # Adds tag to page (if applyTagFlag is True) or removes tag from page (if applyTagFlag is False).
  def setPagesTag(self, page, tag, applyTagFlag):
    pages = CrawlerModelAdapter.extractListParam(pages)
    applyTagFlag =  CrawlerModelAdapter.extractBooleanParam(applyTagFlag)
    self._crawlerModel.setPagesTag(self._activeCrawlerId, pages, tag, applyTagFlag)


  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag):
    terms = CrawlerModelAdapter.extractListParam(terms)
    applyTagFlag =  CrawlerModelAdapter.extractBooleanParam(applyTagFlag)
    self._crawlerModel.setTermsTag(self._activeCrawlerId, terms, tag, applyTagFlag)




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
    delimiter = opt_char if opt_char != None else '|'
    return param.split(delimiter) if len(param) > 0 else []



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
