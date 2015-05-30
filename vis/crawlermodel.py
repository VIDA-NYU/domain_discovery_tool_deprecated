import math
import time
from sklearn.decomposition import PCA
from random import random, randint



class CrawlerModel:
  def __init__(self):
    #TODO(yamuna): Instantiate Elastic Search client, and use the same instance for all queries.
    self._es = None
    self._activeCrawlerId = None
    self._pagesCap = int(10E2)

    # TODO(Yamuna): delete when not returning random data anymore.
    self._randomTerms = {
      'Word': ['Word', randint(1, 100), randint(1, 100), ['Positive']],
      'Disease': ['Disease', randint(1, 100), randint(1, 100), ['Negative']],
      'Control': ['Control', randint(1, 100), randint(1, 100), []],
      'Symptoms': ['Symptoms', randint(1, 100), randint(1, 100), ['Positive']],
      'Epidemy': ['Epidemy', 100, 100, []],
    }



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



  # TODO(cesar): add methods *addCrawler / addSeedCrawler


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



  # Changes the active crawler to be monitored.
  def setActiveCrawler(self, crawlerId):
    self._activeCrawlerId = crawlerId



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
    print '\n\n *** init', opt_ts1

    inc = opt_ts2 - opt_ts1

    print '\n\n *** delta', inc

    factor = 0.1 if opt_applyFilter else 1
    explored = int(factor * (opt_ts1 / 10E6 + inc))
    exploited = int(factor * (opt_ts1 / 10E8 + inc / 2))
    boosted = int(factor * (opt_ts1 / 10E8 + inc / 2))
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
  # TODO(cesar): change return format to include epoch of last downloaded page.
  def getPagesSummarySeedCrawler(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False):
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
    print opt_ts1

    factor = 0.1 if opt_applyFilter else 1
    inc = opt_ts2 - opt_ts1
    relevant = int(factor * (opt_ts1 / 10E6 + inc))
    irrelevant = int(factor * (opt_ts1 / 10E8 + inc / 2))
    neutral = factor * 10E8
    return { \
      'Relevant': relevant,
      'Irrelevant': irrelevant,
      'Neutral': neutral,
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
    # TODO(Yamuna): Query Elastic Search (schema self._activeCrawlerId) for terms ranked by highest
    # tf-idf, and return top opt_maxNumberOfTerms, with tf_idf for term occurring in relevant and
    # irrelevant pages.
    return 9 * self._randomTerms.values()



  # Sets limit to pages returned by @getPages.
  def setPagesCountCap(self, pagesCap):
    # TODO(Yamuna): The cap is just cached, and should be used in getPages (always) and getPagesSummary
    # (when the optional flag is set to True). Check those methods signatures.
    self._pagesCap = int(pagesCap)



  # Returns most recent downloaded pages.
  # Returns dictionary in the format:
  # {
  #   'last_downloaded_url_epoch': 1432310403 (in seconds)
  #   'pages': [
  #             [url1, x, y, tags],     (tags are a list, potentially empty)
  #             [url2, x, y, tags],
  #             [url3, x, y, tags],
  #   ]
  # }
  def getPages(self):
    # TODO(Yamuna): Query Elastic Search (schema self._activeCrawlerId) for downloaded pages, rank
    # them with some criteria, and return the opt_maxNumberOfPages most recent ones.
    # TODO(Yamuna): use self._pagesCap

    print self._pagesCap, '*' * 30, '\n\n'

    now = time.localtime()
    most_current_page = int(time.mktime(now))
    pages = 1000 * [ \
        ['usatoday.com', random(), random(), ['Positive', 'Explored']],
        ['globo.com', random(), random(), []],
        ['cnn.com', random(), random(), ['Positive', 'Exploited']],
        ['news.google.com', random(), random(), ['Positive', 'Boosted']],
        ['bbc.com', random(), random(), ['Relevant']],
        ['wired.com', random(), random(), []],
        ['nydailynews.com', random(), random(), ['Negative']],
        ['cnet.com', random(), random(), ['Negative']],
        ['news.yahoo.com', random(), random(), ['Relevant']],
        ['nbcnews.com', random(), random(), ['Irrelevant']],
    ]
    pages = pages[:self._pagesCap]

    return { \
      'last_downloaded_url_epoch': most_current_page,
      'pages': pages
    }



  # Boosts set of pages: crawler exploits outlinks for the given set of pages in active crawler.
  def boostPages(self, pages):
    # TODO(Yamuna): Issue boostPages on running crawler defined by active crawlerId.
    i = 0
    print 3 * '\n', 'boosted pages', str(pages), 3 * '\n'



  # Fetches snippets for a given term.
  def getTermSnippets(self, term):
    # TODO(Yamuna): Fetch snippets for given term on running crawler defined by active crawlerId.
    snippets = 15 * [3 * 'nho' + ' <em>' + term + '</em> ' + 10 * 'la']
    return {'term': term, 'tags': self._randomTerms[term][3], 'context': snippets}



  # Adds tag to pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  def setPagesTag(self, pages, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.
    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to pages' + str(pages) + '\n\n'
    else:
      print '\n\nremoved tag ' + tag + ' from pages' + str(pages) + '\n\n'



  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  def setTermsTag(self, terms, tag, applyTagFlag):
    # TODO(Yamuna): Apply tag to page and update in elastic search. Suggestion: concatenate tags
    # with semi colon, removing repetitions.
    if applyTagFlag:
      print '\n\napplied tag ' + tag + ' to terms' + str(terms) + '\n\n'
    else:
      print '\n\nremoved tag ' + tag + ' from terms' + str(terms) + '\n\n'
    for term in terms:
      tags = self._randomTerms[term][3]
      tagsSet = set(tags)
      if applyTagFlag:
        tagsSet.add(tag)
      else:
        tagsSet.remove(tag)
      self._randomTerms[term][3] = list(tagsSet)



  # Submits a web query for a list of terms, e.g. 'ebola disease'
  def queryWeb(self, terms):
    # TODO(Yamuna): Issue query on the web.
    i = 0



  # Applies a filter to crawler results, e.g. 'ebola disease'
  def applyFilter(self, terms):
    # TODO(Yamuna): The filter is just cached, and should be used in getPages (always) and getPagesSummary
    # (when the optional flag is set to True). Check those methods signatures.
    self._filter = terms
