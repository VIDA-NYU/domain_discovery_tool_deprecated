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
    self.es = None
    self._activeCrawlerIndex = None
    self._filter = None

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
    # TODO(Yamuna): Fix to point to correct elastic search.
    # Initializes elastic search.
    self.es = ElasticSearch( \
    os.environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in os.environ else 'http://localhost:9200')

    domains = get_available_domains(self.es)
    return \
    [{'id': d['index'], 'name', d['domain_name'], 'creation': d['timestamp']} for d in domains]



  # Returns a list of available seed crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  def getAvailableSeedCrawlers(self):
    # Initializes elastic search.
    self.es = ElasticSearch( \
    os.environ['ELASTICSEARCH_SERVER'] if 'ELASTICSEARCH_SERVER' in os.environ else 'http://localhost:9200')

    domains = get_available_domains(self.es)
    return \
    [{'id': d['index'], 'name', d['domain_name'], 'creation': d['timestamp']} for d in domains]



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
      opt_ts1 = int(time.mktime(now))
    else:
      opt_ts1 = int(opt_ts1)

    # If ts2 not specified, sets it to now.
    if opt_ts2 is None:
      now = time.localtime()
      opt_ts2 = int(time.mktime(now))
    else:
      opt_ts2 = int(opt_ts2)

    if opt_applyFilter:
    # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
      results = \
      range('retrieved',opt_ts1, opt_ts2, ['url','tag'], True, self._activeCrawlerIndex, es=self.es)
    else:
      results = \
      range('retrieved',opt_ts1, opt_ts2, ['url','tag'], True, self._activeCrawlerIndex, es=self.es)

    relevant = 0
    irrelevant = 0
    neutral = 0

    # TODO(Yamuna): Double check the return values for crawler
    for res in results:
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
    # TODO(Yamuna): Query Elastic Search (schema self._activeCrawlerId) for terms ranked by highest
    # tf-idf, and return top opt_maxNumberOfTerms, with tf_idf for term occurring in relevant and
    # irrelevant pages.
    return 9 * self._randomTerms.values()



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
  def getPages(self, opt_maxNumberOfPages = 1000):
    # results are in the format:
    # [["url", "x", "y", "tag", "retrieved"], ... ]
    results = get_most_recent_documents( \
      opt_maxNumberOfPages, self._filter, self._activeCrawlerIndex, es_doc_type = 'page', self.es)

    # Gets last downloaded url epoch from top result (most recent one).
    last_downloaded_url_epoch = 0
    if len(results) > 0:
      last_downloaded_url_epoch = results[0][4]

    # Prepares results: computes projection.
    # TODO(Yamuna): Update x, y for pages after projection is done.
    projectionData = CrawlerModel.projectPages(results)

    # TODO(Yamuna): Fill x and y returned by projection.
    #crawlermodeladapter.runpcasklearn(pos_data, pc_count)

    return { \
    'last_downloaded_url_epoch': last_downloaded_url_epoch,
    'pages': [page[:4] for page in results]
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
    # TODO(Yamuna): Issue query on the web: results are stored in elastic search, nothing returned
    # here.
    i = 0



  # Applies a filter to crawler results, e.g. 'ebola disease'
  def applyFilter(self, terms):
    # The filter is just cached, and should be used in getPages (always) and getPagesSummary
    # (when the optional flag is set to True). Check those methods signatures.
    self._filter = terms


  # Projects pages.
  @staticmethod
  def projectPages(pages):
    return pcaProjectPages(pages)
    
  # Projects pages with PCA.
  @staticmethod
  def pcaProjectPages(pages):
    # TODO(Yamuna): compute tfidf for pages, compute projection, fill x, y.
    dummy = 0.
