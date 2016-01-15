import cherrypy
from ConfigParser import ConfigParser
import json
import os
import urlparse
from crawler_model_adapter import *
from threading import Lock

from bokeh_plots.clustering import selection_plot, empty_plot
from bokeh_plots.domains_dashboard import domains_dashboard

from jinja2 import Template

cherrypy.engine.timeout_monitor.unsubscribe()

class Page:
  @staticmethod
  def getConfig():
    # Parses file to prevent cherrypy from restarting when config.conf changes: after each request
    # it restarts saying config.conf changed, when it did not.
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.conf"))

    configMap = {}
    for section in config.sections():
      configMap[section] = {}
      for option in config.options(section):
        # Handles specific integer entries.
        val = config.get(section, option)
        if option == "server.socket_port" or option == "server.thread_pool":
          val = int(val)
        configMap[section][option] = val

    return configMap


  # Default constructor reading app config file.
  def __init__(self):
    # Folder with html content.
    self._HTML_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), u"html")
    self.lock = Lock()


  # Access to topics visualization.
  @cherrypy.expose
  def topicsvis(self):
    return open(os.path.join(self._HTML_DIR, u"topicsvis.html"))


  # Access to crawler vis.
  @cherrypy.expose
  def crawler(self):
    self._crawler = CrawlerModelAdapter()
    return open(os.path.join(self._HTML_DIR, u"crawlervis.html"))


  # Access to seed crawler vis.
  @cherrypy.expose
  def seedcrawler(self):
    # TODO Use SeedCrawlerModelAdapter self._crawler = SeedCrawlerModelAdapter()
    self._crawler = SeedCrawlerModelAdapter()
    return open(os.path.join(self._HTML_DIR, u"seedcrawlervis.html"))

  @cherrypy.expose
  def release(self):
    return open(os.path.join(self._HTML_DIR, u"release.html"))
  

  @cherrypy.expose
  def index(self):
    return self.seedcrawler()

  # Returns a list of available crawlers in the format:
  # [
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   {'id': crawlerId, 'name': crawlerName, 'creation': epochInSecondsOfFirstDownloadedURL},
  #   ...
  # ]
  @cherrypy.expose
  def getAvailableCrawlers(self):
    res = self._crawler.getAvailableCrawlers()
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)

  @cherrypy.expose
  def getAvailableProjectionAlgorithms(self):
    res = self._crawler.getAvailableProjectionAlgorithms()
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)

  @cherrypy.expose
  def getAvailableQueries(self, session):
    session = json.loads(session)
    res = self._crawler.getAvailableQueries(session)
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)

  # Submits a web query for a list of terms, e.g. 'ebola disease'
  @cherrypy.expose
  def queryWeb(self, terms, session):
    session = json.loads(session)
    self._crawler.queryWeb(terms, session)

  # Add crawler
  @cherrypy.expose
  def addCrawler(self, index_name):
    self._crawler.addCrawler(index_name)

  # Create model
  @cherrypy.expose
  def createModel(self, session):
    session = json.loads(session)
    return self._crawler.createModel(session)
    
  # Returns number of pages downloaded between ts1 and ts2 for active crawler.
  # ts1 and ts2 are Unix epochs (seconds after 1970).
  # If opt_applyFilter is True, the summary returned corresponds to the applied pages filter defined
  # previously in @applyFilter. Otherwise the returned summary corresponds to the entire dataset
  # between ts1 and ts2.
  # 
  # For crawler vis, returns dictionary in the format:
  # {
  #   'Positive': {'Explored': #ExploredPgs, 'Exploited': #ExploitedPgs, 'Boosted': #BoostedPgs},
  #   'Negative': {'Explored': #ExploredPgs, 'Exploited': #ExploitedPgs, 'Boosted': #BoostedPgs},
  # }
  #
  # For seed crawler vis, returns dictionary in the format:
  # {
  #   'Relevant': numPositivePages,
  #   'Irrelevant': numNegativePages,
  #   'Neutral': numNeutralPages,
  # }
  @cherrypy.expose
  def getPagesSummary(self, opt_ts1 = None, opt_ts2 = None, opt_applyFilter = False, session = None):
    session = json.loads(session)
    res = self._crawler.getPagesSummary(opt_ts1, opt_ts2, opt_applyFilter, session)
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)



  # Returns number of terms present in positive and negative pages.
  # Returns array in the format:
  # [
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   [term, frequencyInPositivePages, frequencyInNegativePages],
  #   ...
  # ]
  @cherrypy.expose
  def getTermsSummary(self, session):
    session = json.loads(session)
    res = self._crawler.getTermsSummary(session)
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)

  # Sets limit to pages returned by @getPages.
  @cherrypy.expose
  def setPagesCountCap(self, pagesCap):
    self._crawler.setPagesCountCap(pagesCap)

  # Set the date range to filter data
  @cherrypy.expose
  def setDateTime(self, fromDate=None, toDate=None):
    self._crawler.setDateTime(fromDate, toDate)

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
  @cherrypy.expose
  def getPages(self, session):
    session = json.loads(session)
    res = self._crawler.getPages(session)
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)



  # Boosts set of pages: crawler exploits outlinks for the given set of pages.
  @cherrypy.expose
  def boostPages(self, pages):
    self._crawler.boostPages(pages)


  # Fetches snippets for a given term.
  @cherrypy.expose
  def getTermSnippets(self, term, session):
    session = json.loads(session)
    res = self._crawler.getTermSnippets(term, session)
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)


  # Adds tag to pages (if applyTagFlag is True) or removes tag from pages (if applyTagFlag is
  # False).
  @cherrypy.expose
  def setPagesTag(self, pages, tag, applyTagFlag, session):
    session = json.loads(session)
    self.lock.acquire()
    self._crawler.setPagesTag(pages, tag, applyTagFlag, session)
    self.lock.release()


  # Adds tag to terms (if applyTagFlag is True) or removes tag from terms (if applyTagFlag is
  # False).
  @cherrypy.expose
  def setTermsTag(self, terms, tag, applyTagFlag, session):
    session = json.loads(session)
    self._crawler.setTermsTag(terms, tag, applyTagFlag, session)

  # Delete terms from term window and from the ddt_terms index
  @cherrypy.expose
  def deleteTerm(self, term, session):
    session = json.loads(session)
    self._crawler.deleteTerm(term, session)

  # Download the pages of uploaded urls
  @cherrypy.expose
  def downloadUrls(self, urls, session):
    urls = urls.replace("\n", " ")
    session = json.loads(session)
    self._crawler.downloadUrls(urls, session)

  # Extracts terms with current labels state.
  @cherrypy.expose
  def extractTerms(self, positiveTerms, negativeTerms, neutralTerms):
    res = self._seedCrawler.extractTerms(positiveTerms, negativeTerms, neutralTerms)

    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)


  # Returns available dataset options.
  @cherrypy.expose
  def getAvailableDatasets(self):
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(TrainSetDataLoader._DATASET_OPTIONS.keys())


  # Given dataset name, returns json with term-index and topic-term distributions for +/- examples
  # in training set.
  @cherrypy.expose
  def getTrainingSetTopics(self, datasetName):
    # Data for positive page examples.
    pos = True
    posData = { \
    "topic-term": TrainSetDataLoader.getTopicTermData(datasetName, pos), \
    "topic-cosdistance": TrainSetDataLoader.getCosDistanceData(datasetName, pos), \
    "pca": TrainSetDataLoader.getPCAData(datasetName, pos), \
    "term-index": TrainSetDataLoader.getTermIndexData(datasetName, pos)}

    # Data for negative page examples.
    pos = False
    negData = { \
    "topic-term": TrainSetDataLoader.getTopicTermData(datasetName, pos), \
    "topic-cosdistance": TrainSetDataLoader.getCosDistanceData(datasetName, pos), \
    "pca": TrainSetDataLoader.getPCAData(datasetName, pos), \
    "term-index": TrainSetDataLoader.getTermIndexData(datasetName, pos)}

    # Returns object for positive and negative page examples.
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps({"positive": posData, "negative": negData})

  @cherrypy.expose
  def getBokehPlot(self, session):
    session = json.loads(session)
    data = self._crawler.getPages(session)
    res = {"data": data, "plot": selection_plot(data)}
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)

  @cherrypy.expose
  def getEmptyBokehPlot(self):
    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(empty_plot())

  @cherrypy.expose
  def statistics(self, session):
    session = json.loads(session)
    pages = self._crawler.getPages(session)
    script, div = domains_dashboard(pages)
    with open(os.path.join(self._HTML_DIR, u"domains_dashboard.html")) as f:
        template = Template(f.read())
    return template.render(script=script, div=div)


if __name__ == "__main__":
  page = Page()

  # CherryPy always starts with app.root when trying to map request URIs
  # to objects, so we need to mount a request handler root. A request
  # to "/" will be mapped to HelloWorld().index().
  app = cherrypy.quickstart(page, config=Page.getConfig())
  cherrypy.config.update(page.config)
  #app = cherrypy.tree.mount(page, "/", page.config)

  #if hasattr(cherrypy.engine, "signal_handler"):
  #    cherrypy.engine.signal_handler.subscribe()
  #if hasattr(cherrypy.engine, "console_control_handler"):
  #    cherrypy.engine.console_control_handler.subscribe()
  #cherrypy.engine.start()
  #cherrypy.engine.block()

else:
  page = Page()
  # This branch is for the test suite; you can ignore it.
  app = cherrypy.tree.mount(page, config=Page.getConfig())
