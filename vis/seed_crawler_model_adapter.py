import math
import random
from sklearn.decomposition import PCA
from seed_crawler_model import *

class SeedCrawlerModelAdapter:
  def __init__(self):
    self._seedCrawlerModel = SeedCrawlerModel()
    self._MAX_URL_COUNT = 30
    self._MAX_EXTRACTED_TERMS_COUNT = 40
    self.urls = []
    self.positive_terms_set = set()
    self.negative_terms_set = set()



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

    # Always performs reranking when submitting a query to avoid losing current labels.
    if len(positivePages) > 0 or len(negativePages) > 0:
      positive_pages_list = SeedCrawlerModelAdapter.extractListParam(positivePages)
      negative_pages_list = SeedCrawlerModelAdapter.extractListParam(negativePages)
      self._seedCrawlerModel.submit_selected_urls(positive_pages_list, negative_pages_list)

    # Always updates labels for terms when submitting a query to avoid losing current labels.
    if len(positiveTerms) > 0 or len(negativeTerms) > 0:
      self._updateTermsLabels(positiveTerms, negativeTerms, neutralTerms)

    # Performs query.
    query_term_list = SeedCrawlerModelAdapter.extractListParam(queryTerms, ' ')
    self._seedCrawlerModel.submit_query_terms(query_term_list, self._MAX_URL_COUNT)
    self.urls = list(self._seedCrawlerModel.urls_set)

    print '\n\n\n', '*' * 80
    print 'query_term_list', query_term_list
    print '*' * 80, '\n\n\n'


    # TODO When downloading in parallel, it should wait for pages content to be ready for tf-idf
    # computation.
    # Computes PCA with tf-idf vectors for urls.
    [self.urls, corpus, data] = self._seedCrawlerModel.term_tfidf()
    pc_count = 2
    pcaData = SeedCrawlerModelAdapter.runPCASKLearn(data, pc_count)

    # TODO Read thumbnails.
    positiveUrls = self._seedCrawlerModel.positive_urls_set
    negativeUrls = self._seedCrawlerModel.negative_urls_set
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



  def doRanking(self, positivePages, negativePages):
    positive_pages_list = SeedCrawlerModelAdapter.extractListParam(positivePages)
    negative_pages_list = SeedCrawlerModelAdapter.extractListParam(negativePages)

#    print '\n\n\n', '*' * 80
#    print 'positive_pages_list', positive_pages_list
#    print 'negative_pages_list', negative_pages_list

    rank = self._seedCrawlerModel.submit_selected_urls(positive_pages_list, negative_pages_list)
    print '\n\n\n', '*' * 80
#    print 'positive_pages_list', positive_pages_list
#    print 'negative_pages_list', negative_pages_list
    print rank
    print '\n\n\n', '*' * 80
    # TODO remove test after Yamuna fixes scores computation.
    ranked_urls = rank[0]
    scores = rank[1]
    scores = [random.random() if math.isnan(score) else score for score in scores]
    return {'ranked_urls': ranked_urls, 'scores': scores}



  def _updateTermsLabels(self, positiveTerms, negativeTerms, neutralTerms):
    positive_terms_list = SeedCrawlerModelAdapter.extractListParam(positiveTerms)
    negative_terms_list = SeedCrawlerModelAdapter.extractListParam(negativeTerms)
    neutral_terms_list = SeedCrawlerModelAdapter.extractListParam(neutralTerms)

    self.positive_terms_set = self.positive_terms_set.union(set(positive_terms_list))
    self.negative_terms_set = self.negative_terms_set.union(set(negative_terms_list))

    for neutral_term in neutral_terms_list:
      self.positive_terms_set.discard(neutral_term)
      self.negative_terms_set.discard(neutral_term)

    # Extracts terms and loads their snippets.
    self._seedCrawlerModel.submit_selected_urls([], [])
    self._seedCrawlerModel.submit_selected_terms( \
    list(self.positive_terms_set), list(self.negative_terms_set))



  def extractTerms(self, positiveTerms, negativeTerms, neutralTerms):
    self._updateTermsLabels(positiveTerms, negativeTerms, neutralTerms)

    # Extracts terms and loads their snippets.
    terms = self._seedCrawlerModel.extract_terms(self._MAX_EXTRACTED_TERMS_COUNT)

    new_terms_and_context = {term: self._seedCrawlerModel.term_context([term]) for term in terms}

    terms_and_context = {}
    for term, context in new_terms_and_context.iteritems():
      if term not in self.negative_terms_set:
        terms_and_context[term] = {'term': term, 'context': context, 'label': None}
        if term in self.positive_terms_set:
          terms_and_context[term]['label'] = 'positive'

    return terms_and_context.values()
