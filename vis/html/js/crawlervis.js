/**
 * Visualization for crawler monitoring and steering.
 *
 * April 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */


var CrawlerVis = function() {
};


/**
 * Instantiates for crawler use: inspects crawled pages, lets user tag pages, and boost some pages
 * to steer crawler.
 */
CrawlerVis.buildForCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  var vis = new CrawlerVis();
  vis.initSignalSlotsCrawler.call(vis);
  vis.initUICrawler.call(vis);
  vis.stats = {
    'Positive': {'Exploited': 0, 'Explored': 0, 'New': 0, 'Total': 0},
    'Negative': {'Exploited': 0, 'Explored': 0, 'New': 0, 'Total': 0},
  };
  return vis;
};


/**
 * Instantiates for seed crawler use.
 */
CrawlerVis.buildForSeedCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  var vis = new CrawlerVis();
  vis.initSignalSlotsSeedCrawler.call(vis);
  vis.initUISeedCrawler.call(vis);
  vis.stats = {
    'Relevant': {'Until Last Update': 0, 'New': 0, 'Total': 0},
    'Irrelevant': {'Until Last Update': 0, 'New': 0, 'Total': 0},
    'Neutral': {'Until Last Update': 0, 'New': 0, 'Total': 0},
  };
  return vis;
};


// Initializes signal and slots for crawler use.
CrawlerVis.prototype.initSignalSlotsCrawler = function() {
  SigSlots.connect(
    __sig__.available_crawlers_list_loaded, this, this.createSelectForAvailableCrawlers);
  SigSlots.connect(__sig__.new_pages_summary_fetched, this, this.onLoadedNewPagesSummaryCrawler);
  SigSlots.connect(
    __sig__.previous_pages_summary_fetched, this, this.onLoadedPreviousPagesSummaryCrawler);
  SigSlots.connect(__sig__.terms_summary_fetched, this, this.onLoadedTermsSummary);
  SigSlots.connect(__sig__.term_focus, this, this.onTermFocus);
  SigSlots.connect(__sig__.terms_snippets_loaded, this, this.onLoadedTermsSnippets);
  SigSlots.connect(__sig__.pages_loaded, this, this.onLoadedPages);

  SigSlots.connect(__sig__.tag_focus, this, this.onTagFocus);
  SigSlots.connect(__sig__.tag_clicked, this, this.onTagClicked);
  SigSlots.connect(__sig__.tag_action_clicked, this, this.onTagActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
  SigSlots.connect(__sig__.filter_enter, this, this.runFilter);

  // TODO(Cesar): remove! not active for crawler.
  //SigSlots.connect(__sig__.term_toggle, this, this.onTermToggle);
};


// Initializes signal and slots for seed crawler use.
CrawlerVis.prototype.initSignalSlotsSeedCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  SigSlots.connect(
    __sig__.available_crawlers_list_loaded, this, this.createSelectForAvailableCrawlers);
  SigSlots.connect(__sig__.new_pages_summary_fetched, this, this.onLoadedNewPagesSummarySeedCrawler);
  SigSlots.connect(
    __sig__.previous_pages_summary_fetched, this, this.onLoadedPreviousPagesSummarySeedCrawler);
  SigSlots.connect(__sig__.terms_summary_fetched, this, this.onLoadedTermsSummary);
  SigSlots.connect(__sig__.term_focus, this, this.onTermFocus);
  SigSlots.connect(__sig__.term_toggle, this, this.onTermToggle);
  SigSlots.connect(__sig__.terms_snippets_loaded, this, this.onLoadedTermsSnippets);
  SigSlots.connect(__sig__.pages_loaded, this, this.onLoadedPages);

  SigSlots.connect(__sig__.tag_focus, this, this.onTagFocus);
  SigSlots.connect(__sig__.tag_clicked, this, this.onTagClicked);
  SigSlots.connect(__sig__.tag_action_clicked, this, this.onTagActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
  SigSlots.connect(__sig__.query_enter, this, this.runQuery);
  SigSlots.connect(__sig__.filter_enter, this, this.runFilter);
};


// Initial components setup for seed crawler use.
CrawlerVis.prototype.initUICrawler = function() {
  this.loadAvailableCrawlers();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape(true);
  this.initTagsGallery([
    {'label': 'Positive', 'tag': 'Positive', 'clickable': false},
    {'label': 'Negative', 'tag': 'Negative', 'clickable': false},
    {'label': 'Explored', 'tag': 'Explored', 'clickable': false},
    {'label': 'Boosted', 'tag': 'Boosted', 'clickable': false},
    {'label': 'Exploited', 'tag': 'Exploited', 'clickable': false},
  ]);
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  this.initFilterButton();
};


// Initial components setup for crawler use.
CrawlerVis.prototype.initUISeedCrawler = function() {
  this.loadAvailableCrawlers();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape(false);
  this.initTagsGallery([
    {'label': 'Relevant', 'tag': 'Irrelevant', 'clickable': true},
    {'label': 'Irrelevant', 'tag': 'Irrelevant', 'clickable': true},
    {'label': 'Neutral', 'tag': 'Neutral', 'clickable': true},
  ]);
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  this.initFilterButton();
  this.initQueryWebButton();
};


// Creates select with available crawlers.
CrawlerVis.prototype.createSelectForAvailableCrawlers = function(data) {
  var vis = this;
  var selectBox = d3.select('#selectCrawler').on('change', function() {
    var crawlerId = d3.select(this).node().value;
    vis.setActiveCrawler(crawlerId);
  });
  var getElementValue = function(d) {
    return d.id;
  };
  var options = selectBox.selectAll('option').data(data);
  options.enter().append('option');
  options
    .attr('value', getElementValue)
    .text(function(d, i) {
      // TODO(cesar): Builds string with crawler's name and creation date.
      return d.name + ' (' + Utils.parseFullDate(d.creation) + ')';
    });

  // Manually triggers change of value.
  var crawlerId = getElementValue(data[0]);
  vis.setActiveCrawler(crawlerId);
};


// Loads list of available crawlers.
CrawlerVis.prototype.loadAvailableCrawlers = function() {
  DataAccess.loadAvailableCrawlers();
};


// Sets active crawler.
CrawlerVis.prototype.setActiveCrawler = function(crawlerId) {
  // Changes active crawler and forces update.
  DataAccess.setActiveCrawler(crawlerId);
  DataAccess.update();
};


// Initializes statistics about crawler: number of positive/negative pages,
// exploited/explored/pending for visualization.
CrawlerVis.prototype.initStatslist = function() {
  this.statslist = new Statslist('statslist');
};


// Initializes statistics resulting from filter: number of positive/negative pages,
// exploited/explored/pending for visualization.
CrawlerVis.prototype.initFilterStatslist = function() {
  this.queryStatslist = new Statslist('filter_statslist');
};


// Responds to loaded new pages summary signal (crawler vis).
CrawlerVis.prototype.onLoadedNewPagesSummaryCrawler = function(summary) {
  // All explored and exploited pages are reported as new pages.
  var pos = this.stats['Positive'];
  var neg = this.stats['Negative'];
  pos['New'] =
      summary['Positive']['Exploited']
    + summary['Positive']['Explored'];
  neg['New'] =
      summary['Negative']['Exploited']
    + summary['Negative']['Explored'];

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsCrawler();
};


// Responds to loaded new pages summary signal.
CrawlerVis.prototype.onLoadedNewPagesSummarySeedCrawler = function(summary) {
  var stats = this.stats;
  for (var t in summary) {
    // t is in {Relevant, Irrelevant, Neutral}.
    stats[t]['New'] = summary[t];
    // Computes total.
    stats[t]['Total'] = stats[t]['Until Last Update'] + stats[t]['New'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsSeedCrawler();
};


// Responds to loaded pages summary until last update (crawler vis).
CrawlerVis.prototype.onLoadedPreviousPagesSummaryCrawler = function(summary) {
  var stats = this.stats;

  for (var t in {'Positive': 1, 'Negative': 1}) {
    stats[t]['Explored'] = summary[t]['Explored'];
    stats[t]['Exploited'] = summary[t]['Exploited'];
    stats[t]['Boosted'] = summary[t]['Boosted'];
    // Computes total.
    stats[t]['Total'] = stats[t]['Explored'] + stats[t]['Exploited'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsCrawler();
};


// Responds to loaded pages summary until last update (seed crawler vis).
CrawlerVis.prototype.onLoadedPreviousPagesSummarySeedCrawler = function(summary) {
  var stats = this.stats;

  for (var t in stats) {
    // Stores statistics until last update.
    stats[t]['Until Last Update'] = summary[t];
    // Computes total.
    stats[t]['Total'] = stats[t]['Until Last Update'] + stats[t]['New'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsSeedCrawler();
};


// Updates UI element that reports pages statistics.
CrawlerVis.prototype.updatePagesStatsCrawler = function() {
  var pos = this.stats['Positive'];
  var neg = this.stats['Negative'];

  this.statslist.setEntries([
    {'name': 'Positive pages', 'Explored': pos['Explored'], 'Exploited': pos['Exploited'], 'New': pos['New'], 'label': 'Positive'},
    {'name': 'Negative pages', 'Explored': neg['Explored'], 'Exploited': neg['Exploited'], 'New': neg['New'], 'label': 'Negative'},
  ]);

  // Sets maximum bar width for Positive/Negative pages.
  var maxWidth = Math.max(
    pos['Explored'] + pos['Exploited'] + pos['New'],
    neg['Explored'] + neg['Exploited'] + neg['New']);
  this.statslist.setMaxBarTotal(maxWidth);


  // Updates buttons used to update pages landscape.
  var newPages = pos['New'] + neg['New'];
  d3.select('#pages_landscape_update')
    .classed('enabled', newPages > 0)
    .classed('disabled', newPages == 0);
};


// Updates UI element that reports pages statistics for seed crawler.
CrawlerVis.prototype.updatePagesStatsSeedCrawler = function() {
  var stats = this.stats;

  var entries = [];
  for (var t in stats) {
    // t is in {Relevant, Irrelevant, Neutral}.
    entries.push({
      'name': t + ' pages',
      'Until Last Update': stats[t]['Until Last Update'],
      'New': stats[t]['New'],
      'Total': stats[t]['Total'],
      'label': t,
    });
  }

  // Sets maximum bar width for Positive/Negative pages.
  var maxWidth = Math.max(
    stats['Neutral']['Total'], 
    Math.max(stats['Relevant']['Total'], stats['Irrelevant']['Total']));
  this.statslist.setMaxBarTotal(maxWidth);

  // Updates buttons used to update pages landscape.
  // For seed crawler, update button is always available;
  d3.select('#pages_landscape_update')
    .classed('enabled', true)
    .classed('disabled', false);
};


// Initializes word list: terms with frequency in Positive and Negative pages.
CrawlerVis.prototype.initWordlist = function() {
  this.wordlist = new Wordlist('wordlist');
};


// Initializes pages landscape.
CrawlerVis.prototype.initPagesLandscape = function(showBoostButton) {
  var vis = this;
  this.pagesLandscape = new PagesLandscape('#pages_landscape');

  // Registers action for click on update button.
  d3.select('#pages_landscape_update')
    .on('mouseover', function() {
      Utils.showTooltip();
    })
    .on('mousemove', function() {
      Utils.updateTooltip('Update view with new pages');
    })
    .on('mouseout', function() {
      Utils.hideTooltip();
    })
    .on('click', function() {
      if (!d3.select(this).classed('enabled')) {
        return;
      }
      // Updates pages and terms.
      DataAccess.update();
    });


  if (showBoostButton) {
    // Registers action for click on boost button.
    d3.select('#pages_landscape_boost')
      .on('mouseover', function() {
        Utils.showTooltip();
      })
      .on('mousemove', function() {
        Utils.updateTooltip('Boost selected pages');
      })
      .on('mouseout', function() {
        Utils.hideTooltip();
      })
      .on('click', function() {
        if (!d3.select(this).classed('enabled')) {
          return;
        }
        // Boosts selected pages (items in the gallery).
        var selectedPages = vis.pagesGallery.getItems().map(function(item) {
          // TODO(cesar): use Page Id, not URL.
          return item.url;
        });
        DataAccess.boostPages(selectedPages);
      });
  }
};


// Initializes tags gallery.
CrawlerVis.prototype.initTagsGallery = function(predefinedTags) {
  this.tagsGallery = new TagsGallery('#tags_items', predefinedTags);
};


// Initializes pages gallery (snippets for selected pages).
CrawlerVis.prototype.initPagesGallery = function() {
  this.pagesGallery = new PagesGallery('#pages_items');
};


// Initializes pages gallery (snippets for selected pages).
CrawlerVis.prototype.initTermsSnippetsViewer = function() {
  this.termsSnippetsViewer = new SnippetsViewer('#terms_snippets_viewer');
};


// Responds to loaded terms summary signal.
CrawlerVis.prototype.onLoadedTermsSummary = function(summary) {
  // Updates UI element that reports terms statistics.
  this.wordlist.setEntries(summary.map(function(w) {
    return {'word': w[0], 'posFreq': w[1], 'negFreq': w[2], 'tags': w[3]}
  }));

  // Sets maximum frequency for positive/negative frequencies to set bars width in wordlist.
  var maxPosFreq = d3.max(summary, function(w) { return w[1]; });
  var maxNegFreq = d3.max(summary, function(w) { return w[2]; });
  var maxFreq = Math.max(maxPosFreq, maxNegFreq);
  this.wordlist.setMaxPosNegFreq(maxFreq, maxFreq);

  // Resets terms snippets viewer.
  this.termsSnippetsViewer.clear();
};


// Responds to focus on a term.
CrawlerVis.prototype.onTermFocus = function(term, onFocus) {
  if (onFocus) {
    DataAccess.loadTermSnippets(term);
  }
};


// Responds to toggle of a term.
// Term format:
// {'word': term, 'tags': [], ...}
CrawlerVis.prototype.onTermToggle = function(term, enabled) {
  var vis = this;

  // State machine: Neutral -> Positive -> Negative -> Neutral.
  var tags = term['tags'];
  var isPositive = tags.indexOf('Positive') != -1;
  var isNegative = tags.indexOf('Negative') != -1;

  if (isPositive) {
    // It was positive, so it turns negative.
    DataAccess.setTermTag(term['word'], 'Positive', false);
    DataAccess.setTermTag(term['word'], 'Negative', true);

    // Removes tag 'Positive' from tags array, adds 'Negative'.
    tags.splice(tags.indexOf('Positive'), 1);
    tags.push('Negative');
  }
  else if (isNegative) {
    // It was Negative, so it turns Neutral.
    DataAccess.setTermTag(term['word'], 'Negative', false);

    // Removes tag 'Negative' from tags array.
    tags.splice(tags.indexOf('Negative'), 1);
  }
  else {
    // It was Neutral, so it turns Negative.
    DataAccess.setTermTag(term['word'], 'Positive', true);

    // Adds tag 'Positive' to tags array.
    tags.push('Positive');
  }
  // Updates wordlist.
  vis.wordlist.update();

  // Triggers update of snippets to update its tags.
  __sig__.emit(__sig__.term_focus, term['word'], true);
};


// Responds to loaded terms snippets.
CrawlerVis.prototype.onLoadedTermsSnippets = function(data) {
  var vis = this;

  var term = data.term;
  var tags = data.tags;
  var context = data.context;

  var termObj = {term: term, tags: tags};
  var termSnippets = context.map(function(snippet) {
      return {term: termObj, snippet: snippet};
  });
  var lazyUpdate = true;
  this.termsSnippetsViewer.clear(lazyUpdate);
  this.termsSnippetsViewer.addItems(termSnippets);
};


// Responds to loaded pages signal.
CrawlerVis.prototype.onLoadedPages = function(pagesData) {
  var pages = pagesData['pages'].map(function(page, i) {
    return {
      url: page[0],
      x: page[1],
      y: page[2],
      tags: page[3],
    };
  });
  this.pagesLandscape.setPagesData(pages);

  // Updates last update.
  var lastUpdate = Utils.parseDateTime(DataAccess.getLastUpdateTime());
  d3.select('#last_update_info_box')
    .html('(last update: ' + lastUpdate + ')');

  // Fetches statistics for until last update happened.
  DataAccess.loadPagesSummaryUntilLastUpdate();

  return pages;
};


// Responds to tag focus.
CrawlerVis.prototype.onTagFocus = function(tag, onFocus) {
  // TODO(cesar): focus+context on pages landscape when tag is highlighted.
  console.log('tag highlighted: ', tag, onFocus ? 'gained focus' : 'lost focus');
};


// Responds to clicked tag.
CrawlerVis.prototype.onTagClicked = function(tag) {
  // TODO(cesar): Keep tagged pages on landscape in focus.
  console.log('tag clicked: ', tag);
};


// Responds to clicked tag action.
CrawlerVis.prototype.onTagActionClicked = function(tag, action, opt_items) {
  // If items is empty array, applies action to selected pages in the landscape.
  if (!opt_items || opt_items.length == 0) {
    opt_items = this.pagesLandscape.getSelectedItems();
  }
  // Apply or remove tag from urls.
  var applyTagFlag = 'action' == 'Apply';
  var urls = [];
  for (var i in opt_items) {
    var item = opt_items[i];
    var tags = item.tags;

    // Removes tag when the tag is present for item, and applies only when tag is not present for
    // item.
    var isTagPresent = item.tags.some(function(itemTag) {
      return itemTag == tag;
    });
    if ((applyTagFlag && !isTagPresent) || (!applyTagFlag && isTagPresent)) {
      urls.push(item.url);

      // Updates tag list for items.
      if (applyTagFlag) {
        tags.append(tag);
      } else {
        tags.splice(tags.indexOf(tag), 1);
      }
    }
  }
  DataAccess.setPagesTag(urls, tag, applyTagFlag);
  this.pagesLandscape.update();
  this.pagesGallery.update();
};


/**
 * Responds to new brushing for pages.
 */
CrawlerVis.prototype.onBrushedPagesChanged = function(indexOfSelectedItems) {
  var pages = this.pagesLandscape.getPagesData();
  var selectedPages = indexOfSelectedItems.map(function (index) {
    return pages[index];
  });
  this.pagesGallery.clear();
  this.pagesGallery.addItems(selectedPages);

  // Updates button used to boost selected items in pages landscape.
  d3.select('#pages_landscape_boost')
    .classed('enabled', indexOfSelectedItems.length > 0)
    .classed('disabled', indexOfSelectedItems.length == 0);
};


/**
 * Initializes query web button (useful for seed crawler vis).
 */
CrawlerVis.prototype.initQueryWebButton = function() {
  d3.select('#submit_query')
    .on('click', function() {
      var value = d3.select('#query_box').node().value;
      __sig__.emit(__sig__.query_enter, value);
    });
  // Initializes history of queries.
  this.queriesList = [];
};


/**
 * Initializes filter button.
 */
CrawlerVis.prototype.initFilterButton = function() {
  d3.select('#submit_filter')
    .on('click', function() {
      var value = d3.select('#filter_box').node().value;
      __sig__.emit(__sig__.filter_enter, value);
    });
  // Initializes history of filters.
  this.filtersList = [];
};


/**
 * Runs query (useful for seed crawler vis).
 */
CrawlerVis.prototype.runQuery = function(terms) {
  DataAccess.queryWeb(terms);

  // Appends terms to history of queries.
  this.queriesList =
    this.appendToHistory('#query_box_previous_queries', this.queriesList, terms);
};


/**
 * Runs filter.
 */
CrawlerVis.prototype.runFilter = function(terms) {
  // Applies filter and issues an update automatically.
  DataAccess.applyFilter(terms);
  DataAccess.update();

  // Appends terms to history of filters.
  this.filtersList =
    this.appendToHistory('#filter_box_previous_filters', this.filtersList, terms);
};


/**
 * Appends terms to history of queries/filters.
 * Returns new history.
 */
CrawlerVis.prototype.appendToHistory = function(elementSelector, history, queryTerms) {
  // Appends terms to history of queries/filters.
  var newHistory = [queryTerms].concat(history);
  var previousQueries = d3.select(elementSelector).selectAll('option')
    .data(newHistory, function(d, i) { return queryTerms + '-' + i; });
  previousQueries.enter().append('option');
  previousQueries.exit().remove();
  previousQueries
      .attr('label', function(queryTerms) {
        return queryTerms;
      })
      .attr('value', function(queryTerms) {
        return queryTerms;
      });
  return newHistory;
};
