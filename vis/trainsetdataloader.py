import json
import os

class TrainSetDataLoader:

  # File suffixes and paths.
  _STEM_PATH = 'lda-notstemmed'
  _SUFFIX_TOPIC_TERM_FILE = 'topic-term-distributions.json'
  _SUFFIX_TERM_INDEX_FILE = 'term-index.json'
  _SUFFIX_TOPIC_COSDIST_FILE = 'topic-cosdistance.json'
  _SUFFIX_PCA_FILE = 'pca.json'
  _POSITIVE = '-positive-'
  _NEGATIVE = '-negative-'

  # Path to data files.
  _DATA_FOLDER = os.path.expanduser('./../data')

  # Dataset options (name, alias).
  _DATASET_OPTIONS = {'Ebola': 'ebola', 'Escort': 'escort', 'Human Trafficking': 'ht'}

    
  @staticmethod
  def getAvailableDatasets():
    return TrainSetDataLoader._DATASET_OPTIONS

    
  @staticmethod
  def ensureDatasetIsAvailable(datasetName):
    if not datasetName in TrainSetDataLoader._DATASET_OPTIONS:
      raise Exception('Dataset should be one of ' + str(TrainSetDataLoader._DATASET_OPTIONS.keys()))


  @staticmethod
  def getTopicTermData(datasetName, isPositive):
    return TrainSetDataLoader._getData(\
    datasetName, TrainSetDataLoader._SUFFIX_TOPIC_TERM_FILE, isPositive)


  @staticmethod
  def getCosDistanceData(datasetName, isPositive):
    return TrainSetDataLoader._getData(\
    datasetName, TrainSetDataLoader._SUFFIX_TOPIC_COSDIST_FILE, isPositive)


  @staticmethod
  def getTermIndexData(datasetName, isPositive):
    return TrainSetDataLoader._getData(\
    datasetName, TrainSetDataLoader._SUFFIX_TERM_INDEX_FILE, isPositive)


  @staticmethod
  def getPCAData(datasetName, isPositive):
    return TrainSetDataLoader._getData(\
    datasetName, TrainSetDataLoader._SUFFIX_PCA_FILE, isPositive)


  # Builds filename for training set data.
  @staticmethod
  def _getTrainSetDataFilename(datasetName, fileSuffix, isPositive):
    datasetKey = TrainSetDataLoader._DATASET_OPTIONS[datasetName]
    positiveTerm = TrainSetDataLoader._POSITIVE if isPositive else \
    TrainSetDataLoader._NEGATIVE

    return os.path.join(\
    TrainSetDataLoader._DATA_FOLDER, datasetKey, TrainSetDataLoader._STEM_PATH, \
    datasetKey + positiveTerm + fileSuffix)


  # Given dataset name and file suffix, returns json for +/- examples in training set.
  @staticmethod
  def _getData(datasetName, fileSuffix, isPositive):
    TrainSetDataLoader.ensureDatasetIsAvailable(datasetName)
    try:
      # Reads json and returns.
      fn = TrainSetDataLoader._getTrainSetDataFilename(datasetName, fileSuffix, isPositive)
      with open(fn, 'r') as input_file:
        return json.loads(input_file.read())
    
    except IndexError:
      print 'IndexError: ', datasetName
      # TODO Return http error.
