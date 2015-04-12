import cherrypy
from ConfigParser import ConfigParser
import json
import os
from trainsetdataloader import *
from seed_crawler_model_adapter import *


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
    self._HTML_DIR = os.path.join(os.path.abspath("."), u"html")


  # Access to topics visualization.
  @cherrypy.expose
  def topicsvis(self):
    return open(os.path.join(self._HTML_DIR, u"topicsvis.html"))


  # Access to seed crawler vis.
  @cherrypy.expose
  def seedcrawler(self):
    self._seedCrawler = SeedCrawlerModelAdapter()
    return open(os.path.join(self._HTML_DIR, u"seedcrawlervis.html"))


#  # Submits query for a list of terms.
#  @cherrypy.expose
#  def queryTerms(self, term_list):
#    cherrypy.response.headers["Content-Type"] = "application/json;"
#    #return json.dumps(_seedCrawler.query(term_list))
#    return json.dumps(TrainSetDataLoader._DATASET_OPTIONS.keys())


  # Performs query.
  @cherrypy.expose
  def query( \
  self, queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms):

    res = self._seedCrawler.query( \
    queryTerms, positivePages, negativePages, positiveTerms, negativeTerms, neutralTerms)

    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)


  # Does ranking using newly labeled positive and negative pages.
  @cherrypy.expose
  def doRanking(self, positivePages, negativePages):
    res = self._seedCrawler.doRanking(positivePages, negativePages)

    print "\n\n\n returning"
    print res
    print "\n\n\n"

    cherrypy.response.headers["Content-Type"] = "application/json;"
    return json.dumps(res)


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
