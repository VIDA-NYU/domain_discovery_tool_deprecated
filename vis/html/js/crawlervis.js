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
    'positive': {'exploited': 0, 'explored': 0, 'new': 0},
    'negative': {'exploited': 0, 'explored': 0, 'new': 0},
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
    'positive': {'exploited': 0, 'explored': 0, 'new': 0},
    'negative': {'exploited': 0, 'explored': 0, 'new': 0},
    'neutral': {'exploited': 0, 'explored': 0, 'new': 0},
  };
  return vis;
};


// Initializes signal and slots for crawler use.
CrawlerVis.prototype.initSignalSlotsCrawler = function() {
  SigSlots.connect(
    __sig__.available_crawlers_list_loaded, this, this.createSelectForAvailableCrawlers);
  SigSlots.connect(__sig__.active_crawler_changed, this, this.onActiveCrawlerChanged);
  SigSlots.connect(__sig__.new_pages_summary_fetched, this, this.onLoadedNewPagesSummary);
  SigSlots.connect(__sig__.terms_summary_fetched, this, this.onLoadedTermsSummary);
  SigSlots.connect(__sig__.term_focus, this, this.onTermFocus);
  SigSlots.connect(__sig__.terms_snippets_loaded, this, this.onLoadedTermsSnippets);
  SigSlots.connect(__sig__.pages_loaded, this, this.onLoadedPages);

  SigSlots.connect(__sig__.tag_focus, this, this.onTagFocus);
  SigSlots.connect(__sig__.tag_clicked, this, this.onTagClicked);
  SigSlots.connect(__sig__.tag_action_clicked, this, this.onTagActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
};


// Initializes signal and slots for seed crawler use.
CrawlerVis.prototype.initSignalSlotsSeedCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  SigSlots.connect(
    __sig__.available_crawlers_list_loaded, this, this.createSelectForAvailableCrawlers);
  SigSlots.connect(__sig__.active_crawler_changed, this, this.onActiveCrawlerChanged);
  SigSlots.connect(__sig__.new_pages_summary_fetched, this, this.onLoadedNewPagesSummary);
  SigSlots.connect(__sig__.terms_summary_fetched, this, this.onLoadedTermsSummary);
  SigSlots.connect(__sig__.term_focus, this, this.onTermFocus);
  SigSlots.connect(__sig__.term_toggle, this, this.onTermToggle);
  SigSlots.connect(__sig__.terms_snippets_loaded, this, this.onLoadedTermsSnippets);
  SigSlots.connect(__sig__.pages_loaded, this, this.onLoadedPages);

  SigSlots.connect(__sig__.tag_focus, this, this.onTagFocus);
  SigSlots.connect(__sig__.tag_clicked, this, this.onTagClicked);
  SigSlots.connect(__sig__.tag_action_clicked, this, this.onTagActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
};


// Initial components setup for seed crawler use.
CrawlerVis.prototype.initUICrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  this.loadAvailableCrawlers();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape();
  this.initTagsGallery([
    {'label': 'Positive', 'tag': 'positive', 'clickable': false},
    {'label': 'Negative', 'tag': 'negative', 'clickable': false},
    {'label': 'Explored', 'tag': 'explored', 'clickable': false},
    {'label': 'Boosted', 'tag': 'boosted', 'clickable': false},
    {'label': 'Exploited', 'tag': 'exploited', 'clickable': false},
  ]);
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  // TODO(cesar): add
};


// Initial components setup for crawler use.
CrawlerVis.prototype.initUISeedCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  this.loadAvailableCrawlers();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape();
  this.initTagsGallery([
    {'label': 'Positive', 'tag': 'positive', 'clickable': true},
    {'label': 'Negative', 'tag': 'negative', 'clickable': true},
    {'label': 'Neutral', 'tag': 'neutral', 'clickable': true},
  ]);
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  // TODO(cesar): add
};


// Creates select with available crawlers.
CrawlerVis.prototype.createSelectForAvailableCrawlers = function(data) {
  var selectBox = d3.select('#selectCrawler').on('change', function() {
    var crawlerId = d3.select(this).node().value;
    DataAccess.setActiveCrawler(crawlerId);
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
  DataAccess.setActiveCrawler(getElementValue(data[0]));
};


// Loads list of available crawlers.
CrawlerVis.prototype.loadAvailableCrawlers = function() {
  DataAccess.loadAvailableCrawlers();
};


// Responds to change in active crawler.
CrawlerVis.prototype.onActiveCrawlerChanged = function(crawlerId) {
  this.setActiveCrawler(crawlerId);
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


// Responds to loaded new pages summary signal.
CrawlerVis.prototype.onLoadedNewPagesSummary = function(summary) {
  // All explored and exploited pages are reported as new pages.
  var pos = this.stats['positive'];
  var neg = this.stats['negative'];
  pos['new'] = summary['positive']['exploited'] + summary['positive']['explored'];
  neg['new'] = summary['negative']['exploited'] + summary['negative']['explored'];

  // Updates UI element that reports pages statistics.
  this.updatePagesStats();
};


// Updates UI element that reports pages statistics.
CrawlerVis.prototype.updatePagesStats = function() {
  var pos = this.stats['positive'];
  var neg = this.stats['negative'];

  this.statslist.setEntries([
    {'name': 'Positive pages', 'explored': pos['explored'], 'exploited': pos['exploited'], 'new': pos['new'], 'label': 'positive'},
    {'name': 'Negative pages', 'explored': neg['explored'], 'exploited': neg['exploited'], 'new': neg['new'], 'label': 'negative'},
  ]);

  // Sets maximum bar width for positive/negative pages.
  var maxWidth = Math.max(
    pos['explored'] + pos['exploited'] + pos['new'],
    neg['explored'] + neg['exploited'] + neg['new']);
  this.statslist.setMaxBarTotal(maxWidth);


  // Updates buttons used to update pages landscape.
  var newPages = pos['new'] + neg['new'];
  d3.select('#pages_landscape_update')
    .classed('enabled', newPages > 0)
    .classed('disabled', newPages == 0);

  // Updates last update.
  var lastUpdate = Utils.parseDateTime(DataAccess.getLastUpdateTime());
  d3.select('#last_update_info_box')
    .html('(last update: ' + lastUpdate + ')');
};


// Initializes word list: terms with frequency in positive and negative pages.
CrawlerVis.prototype.initWordlist = function() {
  this.wordlist = new Wordlist('wordlist');
};


// Initializes pages landscape.
CrawlerVis.prototype.initPagesLandscape = function() {
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
    return {'word': w[0], 'posFreq': w[1], 'negFreq': w[2]}
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

  // State machine: neutral -> positive -> negative -> neutral.
  var tags = term['tags'];
  var isPositive = tags.indexOf('positive') != -1;
  var isNegative = tags.indexOf('negative') != -1;

  if (isPositive) {
    // It was positive, so it turns negative.
    DataAccess.setTermTag(term['word'], 'positive', false);
    DataAccess.setTermTag(term['word'], 'negative', true);

    // Removes tag 'positive' from tags array, adds 'negative'.
    tags.splice(tags.indexOf('positive'), 1);
    tags.push('negative');
  }
  else if (isNegative) {
    // It was negative, so it turns neutral.
    DataAccess.setTermTag(term['word'], 'negative', false);

    // Removes tag 'negative' from tags array.
    tags.splice(tags.indexOf('negative'), 1);
  }
  else {
    // It was neutral, so it turns negative.
    DataAccess.setTermTag(term['word'], 'positive', true);

    // Adds tag 'positive' to tags array.
    tags.push('positive');
  }
  // Updates wordlist.
  vis.wordlist.update();
};


// Responds to loaded terms snippets.
CrawlerVis.prototype.onLoadedTermsSnippets = function(data) {
  var vis = this;

  var term = data.term;
  var label = data.label;
  var context = data.context;

  var termObj = {term: term, label: label};
  var termSnippets = context.map(function(snippet) {
      return {term: termObj, snippet: snippet};
  });
  var lazyUpdate = true;
  this.termsSnippetsViewer.clear(lazyUpdate);
  this.termsSnippetsViewer.addItems(termSnippets);
};


// Responds to loaded pages signal.
CrawlerVis.prototype.onLoadedPages = function(pages) {
  var pagesData = [];
  for (var label in pages) {
    // label is positive/negative.
    var labelPages = pages[label];

    // TODO(cesar): separate exploited/explored pages.
    for (var group in labelPages) {
      // Group is exploited/explored.
      var groupPages = labelPages[group];
      // TODO(cesar): concat is not very clever, should reserve and populate.
      pagesData = pagesData.concat(groupPages.map(function(page) {
        return {
          url: page[0],
          label: label,
          group: group,
          x: page[1],
          y: page[2],
        };
      }));
    }
  }
  this.pagesLandscape.setPagesData(pagesData);


  // Consolidates statistics: explored, exploited and new positive/negative pages.
  var pos = this.stats['positive'];
  var neg = this.stats['negative'];
  pos['new'] = neg['new'] = 0;
  pos['exploited'] = pages['positive']['exploited'].length;
  pos['explored'] = pages['positive']['explored'].length;
  neg['exploited'] = pages['negative']['exploited'].length;
  neg['explored'] = pages['negative']['explored'].length;
  this.updatePagesStats();
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
CrawlerVis.prototype.onTagActionClicked = function(tag, action) {
  // TODO(cesar): Tag selected pages on landscape.
  console.log('tag action clicked: ', tag, action);
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
