import math
from models.crawlermodel import *

#
# Base class that defines default functionality for crawler model monitoring/steering.
#
class CrawlerModelAdapter:
  def __init__(self):
    self._crawlerModel = CrawlerModel()



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
    crawlers = sorted(crawlers, key = lambda c: (c['domain_name'], c['timestamp']))
    return [{'id': c['id'], 'name', c['domain_name'], 'creation': c['timestamp']} for c in crawlers]



  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._crawlerModel.setActiveCrawler(crawlerId)



  # Submits a web query for a list of terms, e.g. 'ebola disease'
  def queryWeb(self, terms):
    self._crawlerModel.queryWeb(terms)



  # Applies a filter to crawler results, e.g. 'ebola disease'
  def applyFilter(self, terms):
    self._crawlerModel.applyFilter(terms)



  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # Returns dictionary in the format:
  # {
  #   'Positive': {'Explored': #ExploredPgs, 'Exploited': #ExploitedPgs, 'Boosted': #BoostedPgs},
  #   'Negative': {'Explored': #ExploredPgs, 'Exploited': #ExploitedPgs, 'Boosted': #BoostedPgs},
  # }
  def getPagesSummary(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False):
    return self._crawlerModel.getPagesSummaryCrawler(opt_ts1, opt_ts2, opt_applyFilter)



  # Returns number of terms present in positive and negative pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInPositivePages, frequencyInNegativePages, tags],
  #   [term, frequencyInPositivePages, frequencyInNegativePages, tags],
  #   ...
  # ]
  def getTermsSummary(self):
    return self._crawlerModel.getTermsSummaryCrawler()



  # Returns most recent downloaded pages.
  # Returns dictionary in the format:
  # {
  #   'last_downloaded_url_epoch': 1432310403 (in seconds)
  #   'pages': [
  #             [url1, x, y, tags],     (tags are semicolon separated)
  #             [url2, x, y, tags],
  #             [url3, x, y, tags],
  #   ]
  # }
  def getPages(self, opt_maxNumberOfPages = None):
    return self._crawlerModel.getPages(opt_maxNumberOfPages)



  # Boosts set of pages: crawler exploits outlinks for the given set of pages.
  def boostPages(self, pages):
    pages = CrawlerModelAdapter.extractListParam(pages)
    return self._crawlerModel.boostPages(pages)



  # Fetches snippets for a given term.
  def getTermSnippets(self, term):
    return self._crawlerModel.getTermSnippets(term)



  # Adds tag to page (if applyTagFlag is True) or removes tag from page (if applyTagFlag is False).
  def setPagesTag(self, page, tag, applyTagFlag):
    pages = CrawlerModelAdapter.extractListParam(pages)
    applyTagFlag =  CrawlerModelAdapter.extractBooleanParam(applyTagFlag)
    self._crawlerModel.setPagesTag(pages, tag, applyTagFlag)


  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag):
    terms = CrawlerModelAdapter.extractListParam(terms)
    applyTagFlag =  CrawlerModelAdapter.extractBooleanParam(applyTagFlag)
    self._crawlerModel.setTermsTag(terms, tag, applyTagFlag)



#
# Overwrites default functionality to serve for seed crawler model use.
#
class SeedCrawlerModelAdapter(CrawlerModelAdapter):
  def __init__(self):
    CrawlerModelAdapter.__init__(self)



  # Returns a list of available seed crawlers sorted by name, creation date, in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableCrawlers(self):
    crawlers = self._crawlerModel.getAvailableSeedCrawlers()
    return sorted(crawlers, key = lambda c: (c['name'], c['creation']))



  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # Returns dictionary in the format:
  # {
  #   'Relevant': numPositivePages,
  #   'Irrelevant': numNegativePages,
  #   'Neutral': numNeutralPages,
  # }
  def getPagesSummary(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False):
    return self._crawlerModel.getPagesSummarySeedCrawler(opt_ts1, opt_ts2, opt_applyFilter)



  # Returns number of terms present in relevant and irrelevant pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInRelevantPages, frequencyInIrrelevantPages, tags],
  #   [term, frequencyInRelevantPages, frequencyInIrrelevantPages, tags],
  #   ...
  # ]
  def getTermsSummary(self):
    return self._crawlerModel.getTermsSummarySeedCrawler()


