/**
 * Visualization of topics on the web crawled by a focused crawler.
 *
 * February 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */


// Manages dataset changes: listeners can register with Dataset.addListener(callback(newDataset)).
var Dataset = (function() {
  var listeners = [];

  var pub = {};
  pub.addListener = function(cb) {
    listeners.push(cb);
  };
  pub.onChange = function(value) {
    // Notifies value changed.
    console.log('dataset: ' + value);
    for (var i in listeners) {
      listeners[i](value);
    }
  }
  return pub;
}());
// e.g. of registration of listener of new dataset selection:
//Dataset.addListener(function(newDataset) {
//  console.log('cb1 ' + newDataset);
//});


// Creates select box for available datasets.
var createSelectBox = function(data) {
  var selectBox = d3.select('#selectDataset').on('change', function() {
    Dataset.onChange(d3.select(this).node().value);
  });
  var options = selectBox.selectAll('option').data(data);
  options.enter().append('option');
  options
    .attr('value', function(d, i) { return d; })
    .text(function(d, i) { return d; });

  // Manually triggers change of value.
  Dataset.onChange(data[0]);
};


var loadTrainingSetData = function(newDataset, cb) {
  // Gets topics for training set.
  Utils.setWaitCursorEnabled(true);
  $.post(
    '/getTrainingSetTopics',
    {
      'datasetName': newDataset,
    },
    function(data) {
      // ******************************************    ********************************************************************

      // TODO (cesar): remove when Kien compute relevant terms with termite code by Stanford.
      var maxTermsCount = 30;
      var pageTypes = ['positive', 'negative'];
      for (var typeIndex in pageTypes) {
        var pageType = pageTypes[typeIndex];

        // Resizes vocabulary.
        data[pageType]['term-index'].length = maxTermsCount;
        // Resizes term-distribution per topic.
        for (var topicIndex in data[pageType]['topic-term']) {
          data[pageType]['topic-term'][topicIndex].length = maxTermsCount;
        }
      }

      // ******************************************    ********************************************************************

      Utils.setWaitCursorEnabled(false);
      cb(data);
    }
  );
};


// Sets up user interface elements. Should be called only once.
var setupUI = function() {
  // Initialize termite for positive/negative topics.
  posTermite = new Termite('termite_pos_container');
  negTermite = new Termite('termite_neg_container', true);

  // Initialize heatmap for cosine distance between positive/negative topics.
  posHeatMap = new HeatMap('heatmap_pos_container');
  negHeatMap = new HeatMap('heatmap_neg_container', true);

  // Initializes bubble charts for positive and negative topics.
  posBubbleChart = new BubbleChart('pos_topics_map_container');
  negBubbleChart = new BubbleChart('neg_topics_map_container');

  tagCloud1 = new TagCloud('tagCloud1');

  // Registers for dataset change event.
  Dataset.addListener(function(newDataset) {
    // Loads dataset.
    loadTrainingSetData(newDataset, function(data) {
      // Redraws visualizations.
      var pos = data['positive'],
          neg = data['negative'];

      // Draws termite for positive and negative example pages.
      posTermite.draw(pos['topic-term'], pos['term-index'], 'Positive topics');
      negTermite.draw(neg['topic-term'], neg['term-index'], 'Negative topics');

      // Draws heat map for cosine distance for positive and negative example pages.
      posHeatMap.draw(pos['topic-cosdistance'], 'Cosine distance');
      negHeatMap.draw(neg['topic-cosdistance'], 'Cosine distance');

      // TODO(cesar) Use PCA results.
      // Draws bubble charts for positive and negative example pages.
      posBubbleChart.draw(pos['topic-term'], pos['term-index'], pos['pca']);
      negBubbleChart.draw(neg['topic-term'], neg['term-index'], neg['pca']);
    });
  });

  // Gets available datasets.
  $.post(
    '/getAvailableDatasets',
    {},
    function(datasets) {
      createSelectBox(datasets);
    }
  );
};


// TODO (cesar): Glue all interaction between panels into a single controller.
var onSelectTopic = function(topicDistribution, terms) {
    // TODO Redraw tag cloud on topic selection.
    tagCloud1.draw(createTagCloudData(topicDistribution, terms));
};


// Initializes the page.
var initialize = function() {
  setupUI();
};

window.onload = initialize;
