/**
 * Visualization for seed crawler.
 *
 * April 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */

var SeedCrawlerVis = function() {
  this.queriesList = [];
  this.pagesGallery = new PagesGallery('#pages_items');
  //this.pagesControls = new PagesControls();
  this.termsGallery = new TermsGallery('#terms_items');
  this.pagesLandscape = new PagesLandscape('#pages_landscape');
  this.snippetsViewer = new SnippetsViewer('#snippets_viewer');

  // Registers signal/slots.
  SigSlots.connect(
    __sig__.pages_labels_changed, this.pagesLandscape, this.pagesLandscape.onPageLabelsChanged);

  // TODO


  // Populates pagesGallery with items read from backend.
  //// TODO


  //// TODO remove this test.
  //var pagesSeeds = [
  //  {url: 'www.espn.com', thumbnail: 'img/thumb1.jpg'},
  //  {url: 'www.nyu.edu', thumbnail: 'img/thumb2.jpg'},
  //  {url: 'www.cbs.com', thumbnail: 'img/thumb3.jpg'},
  //  {url: 'www.gmail.com', thumbnail: 'img/thumb4.jpg'},
  //  {url: 'www.yahoo.com', thumbnail: 'img/thumb5.jpg'},
  //  {url: 'www.bing.com', thumbnail: 'img/thumb6.jpg'},
  //  {url: 'www.usatoday.com', thumbnail: 'img/thumb7.jpg'},
  //];
  //var pagesEntries = d3.range(14).map(function() {
  //  var entry = pagesSeeds[Utils.getRandomInt(0, pagesSeeds.length)];
  //  return {url: entry.url, thumbnail: entry.thumbnail};
  //});
  //pagesEntries = PagesLandscape.createRandomPositions(pagesEntries);
  //this.pagesGallery.addItems(pagesEntries);

  //// Populates pages landscape with items read from backend.
  //this.pagesLandscape.setPagesData(pagesEntries);

  //// Populates termsGallery with items read from backend.
  //// TODO


  //// TODO remove this test.
  //var lazyUpdate = true;
  //var termsGallery = this.termsGallery;
  //['government', 'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life', 'hand',
  //    'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case', 'point', 'company',
  //    'number', 'group', 'problem', 'fact', 'Verbs', 'be', 'have', 'do', 'say', 'get', 'make', 'go',
  //    'know', 'take', 'see', 'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask',
  //    'work', 'seem', 'feel', 'try', 'leave', 'call',
  //].map(function(term, i) {
  //  termsGallery.addItem({term: term}, lazyUpdate);
  //});
  //this.termsGallery.update();


  //// TODO remove test (move to a SnippetsBuilder class).
  //var prefixesOrSuffixes = ['nhonhonho', 'blablabla', 'dududu', 'ipsum'];
  //var snippetsViewer = this.snippetsViewer;
  //var showSnippets = function(term) {
  //  var snippets = d3.range(6).map(function() {
  //    var prefix = d3.range(4).map(function() {
  //      return prefixesOrSuffixes[Utils.getRandomInt(0, prefixesOrSuffixes.length)];
  //    });
  //    var suffix = d3.range(4).map(function() {
  //      return prefixesOrSuffixes[Utils.getRandomInt(0, prefixesOrSuffixes.length)];
  //    });
  //    var termContent = '<em class=\"' + term.label + '\">' + term.term + '</em>';
  //    var content = prefix.concat([termContent]).concat(suffix);
  //    return {term: term.term, snippet: content.join(' ')};
  //  });
  //  snippetsViewer.clear(lazyUpdate);
  //  snippetsViewer.addItems(snippets, lazyUpdate);
  //  snippetsViewer.update();
  //};
  //SigSlots.connect(__sig__.term_selected, this, showSnippets);

  SigSlots.connect(__sig__.term_selected, this, this.showSnippets);

  // Registers event for enter press on query textfield.
  d3.select('#query_box')
    .on('keydown', function() {
      if (d3.event.keyCode === 13) {
        __sig__.emit(__sig__.query_enter, this.value);
      }
    });
  d3.select('#submit_query')
    .on('click', function() {
      var value = d3.select('#query_box').node().value;
      __sig__.emit(__sig__.query_enter, value);
    });
  SigSlots.connect(__sig__.query_enter, this, this.runQuery);
  SigSlots.connect(__sig__.pages_do_ranking, this, this.doRanking);
  SigSlots.connect(__sig__.pages_extract_terms, this, this.extractTerms);
  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
  SigSlots.connect(__sig__.add_term_to_query_box, this, this.addTermToQueryBox);
};


/**
 * Runs query for given terms.
 */
SeedCrawlerVis.prototype.runQuery = function(queryTerms) {
  var vis = this;
  Utils.setWaitCursorEnabled(true);

  // Append to beginning.
  this.queriesList = [queryTerms].concat(this.queriesList);
  var previousQueries = d3.select('#query_box_previous_queries').selectAll('option')
    .data(this.queriesList, function(d, i) { return queryTerms + '-' + i; });
  previousQueries.enter().append('option');
  previousQueries.exit().remove();
  previousQueries
      .attr('label', function(queryTerms) {
        return queryTerms;
      })
      .attr('value', function(queryTerms) {
        return queryTerms;
      });

  // Extracts positive/negative pages, since ranking is done with every query.
  var pages = this.pagesLandscape.getPagesData();
  var positivePages = pages.filter(function(item, i) {
    return item.label === 'positive';
  }).map(function(item) { return item.url; });
  var negativePages = pages.filter(function(item, i) {
    return item.label === 'negative';
  }).map(function(item) { return item.url; });

  // Extracts positive/negative terms, since terms labeling is done with every query.
  var terms = this.termsGallery.getItems();
  var positiveTerms = terms.filter(function(item, i) {
    return item.label === 'positive';
  }).map(function(item) { return item.term; });
  var negativeTerms = terms.filter(function(item, i) {
    return item.label === 'negative';
  }).map(function(item) { return item.term; });
  var neutralTerms = terms.filter(function(item, i) {
    return item.label === undefined;
  }).map(function(item) { return item.term; });


  // Performs query using ajax.
  $.post(
    '/query',
    {
      'queryTerms': queryTerms,
      'positivePages': positivePages.join('|'),
      'negativePages': negativePages.join('|'),
      'positiveTerms': positiveTerms.join('|'),
      'negativeTerms': negativeTerms.join('|'),
      'neutralTerms': neutralTerms.join('|'),
    },
    function(data) {
      //console.log(data.urls);
      var pcaPositions = data.pcaData[1];

      var pagesEntries = data.urls.map(function(urlInfo, i) {
        var pointPosition = pcaPositions[i];

        // TODO use thumbnail when computed.
        return {
          url: urlInfo.url,
          thumbnail: urlInfo.thumbnail || 'img/defaultThumbnail.jpg',
          label: urlInfo.label,
          x: pointPosition[0],
          y: pointPosition[1],
        };
      });

      // Populates pages landscape with items read from backend and clears pages gallery.
      // TODO(cesar): set pages or add pages?
      vis.pagesLandscape.setPagesData(pagesEntries);
      vis.pagesGallery.clear();

      Utils.setWaitCursorEnabled(false);


      // When done running query, extracts terms automatically.
      vis.extractTerms.call(vis);
    }
  );
  
};


/**
 * Does ranking with current state for pages labels.
 */
SeedCrawlerVis.prototype.doRanking = function() {
  var vis = this;
  Utils.setWaitCursorEnabled(true);

  var pages = this.pagesLandscape.getPagesData();
  var positivePages = pages.filter(function(item, i) {
    return item.label === 'positive';
  }).map(function(item) { return item.url; });
  var negativePages = pages.filter(function(item, i) {
    return item.label === 'negative';
  }).map(function(item) { return item.url; });

  $.post(
    '/doRanking',
    {
      'positivePages': positivePages.join('|'),
      'negativePages': negativePages.join('|'),
    },
    function(data) {
      console.log(data);
      // Recommends positive labels.
      // TODO Recommend negative labels.
      var allUrls = vis.pagesLandscape.getPagesData().reduce(function(o, d, i) {
        o[d.url] = d;
        return o;
      }, {});

      var SCORE_THRESHOLD = 0.5;
      var OPACITY_PENALTY = 0.0;
      data.ranked_urls.forEach(function(rankedUrl, i) {
        if (!(rankedUrl in allUrls)) {
          console.log('Check with Yamuna why');
        } else {
          var score = data.scores[i];
          console.log(score);
          if (score > SCORE_THRESHOLD) {
            // Positive recommendation.
            // TODO Use returned score after Yamuna fixes ranking scores.
            allUrls[rankedUrl].label = 'positive_recommendation';
            allUrls[rankedUrl].opacity = score - OPACITY_PENALTY;
          } else {
            // Negative recommendation.
            // TODO Use returned score after Yamuna fixes ranking scores.
            allUrls[rankedUrl].label = 'negative_recommendation';
            allUrls[rankedUrl].opacity = 1.0 - score - OPACITY_PENALTY;
          }
        }
      });
      vis.pagesLandscape.update();
      vis.pagesGallery.update();

      Utils.setWaitCursorEnabled(false);
    }
  );
};


/**
 * Extracts terms using current state for pages labels and ranking.
 */
SeedCrawlerVis.prototype.extractTerms = function() {
  var vis = this;
  Utils.setWaitCursorEnabled(true);

  var terms = this.termsGallery.getItems();
  var positiveTerms = terms.filter(function(item, i) {
    return item.label === 'positive';
  }).map(function(item) { return item.term; });
  var negativeTerms = terms.filter(function(item, i) {
    return item.label === 'negative';
  }).map(function(item) { return item.term; });
  var neutralTerms = terms.filter(function(item, i) {
    return item.label === undefined;
  }).map(function(item) { return item.term; });

  $.post(
    '/extractTerms',
    {
      'positiveTerms': positiveTerms.join('|'),
      'negativeTerms': negativeTerms.join('|'),
      'neutralTerms': neutralTerms.join('|'),
    },
    function(data) {
      //console.log(data);

      // TODO Move to a SnippetsBuilder class.
      vis.snippets = {};
      var lazyUpdate = true;
      vis.termsGallery.clear(lazyUpdate);

      data.forEach(function(entry) {
        var term = entry.term;
        var label = entry.label;
        var context = entry.context;

        var termObj = {term: term, label: label};
        var termSnippets = context.map(function(snippet) {
          return {term: termObj, snippet: snippet[0]};
        });

        vis.snippets[term] = termSnippets;
        vis.termsGallery.addItem(termObj, lazyUpdate);
      });
      vis.termsGallery.update();
      var snippetsViewer = vis.snippetsViewer;
      snippetsViewer.clear();

      Utils.setWaitCursorEnabled(false);
    }
  );
};


/**
 * Shows snippets for a given term.
 */
SeedCrawlerVis.prototype.showSnippets = function(term) {
  var lazyUpdate = true;
  this.snippetsViewer.clear(lazyUpdate);
  this.snippetsViewer.addItems(this.snippets[term.term]);
};


/**
 * Responds to new brushing for pages.
 */
SeedCrawlerVis.prototype.onBrushedPagesChanged = function(indexOfSelectedItems) {
  var pages = this.pagesLandscape.getPagesData();
  var selectedPages = indexOfSelectedItems.map(function (index) {
    return pages[index];
  });
  this.pagesGallery.clear();
  this.pagesGallery.addItems(selectedPages);
};


/**
 * Adds term to query box.
 */
SeedCrawlerVis.prototype.addTermToQueryBox = function(term) {
  var boxElem = d3.select('#query_box').node();
  boxElem.value += ' ' + term;
};


window.onload = function() {
  new SeedCrawlerVis();
};
