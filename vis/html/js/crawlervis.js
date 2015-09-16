/**
 * Visualization for crawler monitoring and steering.
 *
 * April 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */

var CrawlerVis = function() {
    var currentCrawler = undefined;
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
  vis.filterStats = {
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
  vis.filterStats = {
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
  SigSlots.connect(
    __sig__.available_crawlers_list_reloaded, this, this.reloadSelectForAvailableCrawlers);
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
  SigSlots.connect(
    __sig__.tag_individual_page_action_clicked, this, this.onTagIndividualPageActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
  SigSlots.connect(__sig__.filter_enter, this, this.runFilter);
  SigSlots.connect(__sig__.add_term, this, this.runAddTerm);
  SigSlots.connect(__sig__.add_neg_term, this, this.runAddNegTerm);
  SigSlots.connect(__sig__.load_new_pages_summary, this, this.loadNewPagesSummary);
    
  // TODO(Cesar): remove! not active for crawler.
  //SigSlots.connect(__sig__.term_toggle, this, this.onTermToggle);
};


// Initializes signal and slots for seed crawler use.
CrawlerVis.prototype.initSignalSlotsSeedCrawler = function() {
  // TODO(cesar): review function calls to see if all slots/UI elements are created correctly.
  SigSlots.connect(
    __sig__.available_crawlers_list_loaded, this, this.createSelectForAvailableCrawlers);
  SigSlots.connect(
    __sig__.available_crawlers_list_reloaded, this, this.reloadSelectForAvailableCrawlers);
  SigSlots.connect(
    __sig__.available_proj_alg_list_loaded, this, this.createSelectForAvailableProjectionAlgorithms);
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
  SigSlots.connect(
    __sig__.tag_individual_page_action_clicked, this, this.onTagIndividualPageActionClicked);

  SigSlots.connect(__sig__.brushed_pages_changed, this, this.onBrushedPagesChanged);
  SigSlots.connect(__sig__.add_crawler, this, this.runAddCrawler);
  SigSlots.connect(__sig__.query_enter, this, this.runQuery);
  SigSlots.connect(__sig__.filter_enter, this, this.runFilter);
  SigSlots.connect(__sig__.add_term, this, this.runAddTerm);
  SigSlots.connect(__sig__.add_neg_term, this, this.runAddNegTerm);
  SigSlots.connect(__sig__.delete_term, this, this.runDeleteTerm);
  SigSlots.connect(__sig__.load_new_pages_summary, this, this.loadNewPagesSummary);
};


// Initial components setup for seed crawler use.
CrawlerVis.prototype.initUICrawler = function() {
  this.loadAvailableCrawlers();
  this.loadAvailableProjectionAlgorithms();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape(true);
  this.initTagsGallery(
    [
      'Relevant',
      'Irrelevant',
      'Neutral',
      'Positive',
      'Negative',
      'Explored',
      'Boosted',
      'Exploited',
    ],
    {
      'Relevant': {
        applicable: true,
        removable: true,
        negate: ['Irrelevant'],
      },
      'Irrelevant': {
        applicable: true,
        removable: true,
        negate: ['Relevant'],
      },
      'Neutral': {
        isVirtual: true,
        applicable: true,
        removable: false,
        negate: ['Relevant', 'Irrelevant'],
      },
      'Positive': {
        applicable: false,
        removable: false,
        negate: [],
      },
      'Negative': {
        applicable: false,
        removable: false,
        negate: [],
      },
      'Explored': {
        applicable: false,
        removable: false,
        negate: [],
      },
      'Exploited': {
        applicable: false,
        removable: false,
        negate: [],
      },
      'Boosted': {
        applicable: false,
        removable: false,
        negate: [],
      },
    });
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  this.initFilterButton();
  this.initModelButton();
  this.createSelectForFilterPageCap();
};


// Initial components setup for crawler use.
CrawlerVis.prototype.initUISeedCrawler = function() {
  this.loadAvailableCrawlers();
  this.loadAvailableProjectionAlgorithms();
  this.initWordlist();
  this.initStatslist();
  this.initFilterStatslist();
  this.initPagesLandscape(false);
  this.initTagsGallery(
    [
      'Relevant',
      'Irrelevant',
      'Neutral',
    ],
    {
      'Relevant': {
        applicable: true,
        removable: true,
        negate: ['Irrelevant'],
      },
      'Irrelevant': {
        applicable: true,
        removable: true,
        negate: ['Relevant'],
      },
      'Neutral': {
        isVirtual: true,
        applicable: true,
        removable: false,
        negate: ['Relevant', 'Irrelevant'],
      },
    });
  this.initPagesGallery();
  this.initTermsSnippetsViewer();
  this.initFilterButton();
  this.initModelButton();
  this.initQueryWebButton();
  this.initAddCrawlerButton();
  this.initFromCalendarButton();
  this.initToCalendarButton();
  this.createSelectForFilterPageCap();
  this.initAddTermButton();
};

CrawlerVis.prototype.getElementValueId = function(d){
  return d.id;
}

CrawlerVis.prototype.setCurrentCrawler = function(crawlerId){
  this.currentCrawler = crawlerId;
  this.setActiveCrawler(crawlerId)
}

CrawlerVis.prototype.renderCrawlerOptions = function(element, data, selectedCrawler){
  var vis = this;

  // Remove existing crawler options before rendering new ones.
  element.selectAll('li').filter(function(d, i){
    return (this.id != "addDomainButton");
  }).remove();
  var options = element.selectAll('input').data(data);
  options.enter().append('input');
  options
    .attr('value', vis.getElementValueId)
    .attr('type', 'radio')
    .attr('name', 'crawlerRadio')
    .attr('id', vis.getElementValueId)
    .attr('placeholder', function(d, i){
      // return d.name + ' (' + Utils.parseFullDate(d.creation) + ')'
      return d.name
    })

  // Wrap each input and give it a label.
  d3.selectAll("input[name='crawlerRadio']").each(function(){
    $("input[id='"+this.id+"']")
      .wrap("<li class='crawler-radio'></li>")
      .after("<label for='"+this.id+"'>"+this.placeholder+"</label>");
  });
  if (selectedCrawler){
    d3.select('input[value="'+selectedCrawler+'"]').attr("checked", "checked");
  }

  d3.selectAll('input[name="crawlerRadio"]').on('change', function(){
    var crawlerId = d3.select('input[name="crawlerRadio"]:checked').node().value;
    vis.setCurrentCrawler(crawlerId);
  });

  // Add the Add Domain button after the last element in the crawler selection.
  var addDomain = $("#addDomainButton").detach();
  addDomain.appendTo($("#selectCrawler:last-child"));
}

// Creates select with available crawlers.
CrawlerVis.prototype.createSelectForAvailableCrawlers = function(data) {
  var vis = this;
  var selectBox = d3.select('#selectCrawler');

  if (data.length > 0){
    vis.renderCrawlerOptions(selectBox, data);
    // Manually triggers change of value.
    var crawlerId = vis.getElementValueId(data[0]);
    vis.setCurrentCrawler(crawlerId);
    d3.select('input[value="'+data[0]["id"]+'"]').attr("checked", "checked");
    $("#currentDomain").text(data[0].name).append("<span class='caret'></span>");
  } else {
    $("#currentDomain").text("Select/Add Domains").append("<span class='caret'></span>");
    document.getElementById("status_panel").innerHTML = 'No domains found'
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
  }
}

// Reload select with available crawlers.
CrawlerVis.prototype.reloadSelectForAvailableCrawlers = function(data) {
  if (data.length > 0) {
    var vis = this;
    var selectBox = d3.select('#selectCrawler');
    var selectedCrawler = d3.select('input[name="crawlerRadio"]:checked').node()

    // Generate the index name from the entered crawler name
    var index_name = d3.select('#crawler_index_name').node().value;

    // If just one crawler exists then select that
    if (selectedCrawler){
      vis.renderCrawlerOptions(selectBox, data, selectedCrawler.id);
      $("#currentDomain").text(selectedCrawler.placeholder).append("<span class='caret'></span>");
    } else {
      var crawlerId = vis.getElementValueId(data[0]);
      vis.setCurrentCrawler(crawlerId);
      vis.renderCrawlerOptions(selectBox, data, crawlerId);
      $("#currentDomain").text(data[0]["name"]).append("<span class='caret'></span>");
    }

    document.getElementById("status_panel").innerHTML = 'Added new domain - ' + index_name;
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));

  } else {
    document.getElementById("status_panel").innerHTML = 'No domains found';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
  }
};



// Loads list of available crawlers.
CrawlerVis.prototype.loadAvailableCrawlers = function() {
  DataAccess.loadAvailableCrawlers();
};


// Sets active crawler.
CrawlerVis.prototype.setActiveCrawler = function(crawlerId) {
    $("#wordlist").html("");

    this.initWordlist();

    this.termsSnippetsViewer.clear();

    // Changes active crawler and forces update.
    DataAccess.setActiveCrawler(crawlerId);
    
    d3.select('#filter_box').node().value = "";
};


// Creates select with available projection algorithms.
CrawlerVis.prototype.createSelectForAvailableProjectionAlgorithms = function(data) {
  var vis = this;
  var selectBox = d3.select('#selectProjectionAlgorithm').on('change', function() {
      var algId = d3.select(this).node().value;
      vis.setActiveProjectionAlg(algId);
  });
  var getElementValue = function(d) {
    return d.name;
  };
  var options = selectBox.selectAll('option').data(data);
  options.enter().append('option');
  options
    .attr('value', getElementValue)
    .text(function(d, i) {
      return d.name;
    });

  $('#selectProjectionAlgorithm').val("PCA")
};


// Loads list of available projection algorithms.
CrawlerVis.prototype.loadAvailableProjectionAlgorithms = function() {
  DataAccess.loadAvailableProjectionAlgorithms();
};


// Sets active projection algorithm.
CrawlerVis.prototype.setActiveProjectionAlg = function(algId) {
  // Changes active crawler and forces update.
  DataAccess.setActiveProjectionAlg(algId);
};


// Initializes statistics about crawler: number of positive/negative pages,
// exploited/explored/pending for visualization.
CrawlerVis.prototype.initStatslist = function() {
  this.statslist = new Statslist('statslist');
};


// Initializes statistics resulting from filter: number of positive/negative pages,
// exploited/explored/pending for visualization.
CrawlerVis.prototype.initFilterStatslist = function() {
  this.filterStatslist = new Statslist('filter_statslist');
};


// Responds to loaded new pages summary signal (crawler vis).
CrawlerVis.prototype.onLoadedNewPagesSummaryCrawler = function(summary, isFilter) {
  var stats = isFilter ? this.filterStats : this.stats;
  var statslist = isFilter ? this.filterStatslist : this.statslist;

  // All explored and exploited pages are reported as new pages.
  var pos = stats['Positive'];
  var neg = stats['Negative'];
  pos['New'] =
      summary['Positive']['Exploited']
    + summary['Positive']['Explored'];
  neg['New'] =
      summary['Negative']['Exploited']
    + summary['Negative']['Explored'];

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsCrawler(stats, statslist);
};


// Responds to loaded pages summary until last update (crawler vis).
CrawlerVis.prototype.onLoadedPreviousPagesSummaryCrawler = function(summary, isFilter) {
  var stats = isFilter ? this.filterStats : this.stats;
  var statslist = isFilter ? this.filterStatslist : this.statslist;

  for (var t in {'Positive': 1, 'Negative': 1}) {
    stats[t]['Explored'] = summary[t]['Explored'];
    stats[t]['Exploited'] = summary[t]['Exploited'];
    stats[t]['Boosted'] = summary[t]['Boosted'];
    // Computes total.
    stats[t]['Total'] = stats[t]['Explored'] + stats[t]['Exploited'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsCrawler(stats, statslist);
};


// Updates UI element that reports pages statistics.
CrawlerVis.prototype.updatePagesStatsCrawler = function(stats, statslist) {
  var pos = stats['Positive'];
  var neg = stats['Negative'];

  statslist.setEntries([
    {'name': 'Positive pages', 'Explored': pos['Explored'], 'Exploited': pos['Exploited'], 'New': pos['New'], 'label': 'Positive'},
    {'name': 'Negative pages', 'Explored': neg['Explored'], 'Exploited': neg['Exploited'], 'New': neg['New'], 'label': 'Negative'},
  ]);

  // Sets maximum bar width for Positive/Negative pages.
  var maxWidth = Math.max(
    pos['Explored'] + pos['Exploited'] + pos['New'],
    neg['Explored'] + neg['Exploited'] + neg['New']);
  statslist.setMaxBarTotal(maxWidth);


  // Updates buttons used to update pages landscape.
  var newPages = pos['New'] + neg['New'];
  d3.select('#pages_landscape_update')
    .classed('enabled', newPages > 0)
    .classed('disabled', newPages == 0);
};


// Responds to loaded new pages summary signal.
CrawlerVis.prototype.onLoadedNewPagesSummarySeedCrawler = function(summary, isFilter) {
  var stats = isFilter ? this.filterStats : this.stats;
  var statslist = isFilter ? this.filterStatslist : this.statslist;

  for (var t in summary) {
    // t is in {Relevant, Irrelevant, Neutral}.
    stats[t]['New'] = summary[t];
    // Computes total.
    stats[t]['Total'] = stats[t]['Until Last Update'] + stats[t]['New'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsSeedCrawler(stats, statslist);
};


// Responds to loaded pages summary until last update (seed crawler vis).
CrawlerVis.prototype.onLoadedPreviousPagesSummarySeedCrawler = function(summary, isFilter) {
  var stats = isFilter ? this.filterStats : this.stats;
  var statslist = isFilter ? this.filterStatslist : this.statslist;

  for (var t in stats) {
    // t is in {Relevant, Irrelevant, Neutral}.
    // Stores statistics until last update.
    stats[t]['Until Last Update'] = summary[t];
    // Computes total.
    stats[t]['Total'] = stats[t]['Until Last Update'] + stats[t]['New'];
  }

  // Updates UI element that reports pages statistics.
  this.updatePagesStatsSeedCrawler(stats, statslist);
};


// Updates UI element that reports pages statistics for seed crawler.
CrawlerVis.prototype.updatePagesStatsSeedCrawler = function(stats, statslist) {
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
  var lazyUpdate = true;
  statslist.setEntries(entries, lazyUpdate);


  // Sets maximum bar width for Positive/Negative pages.
  var maxWidth = Math.max(
    stats['Neutral']['Total'], 
    Math.max(stats['Relevant']['Total'], stats['Irrelevant']['Total']));
  statslist.setMaxBarTotal(maxWidth);

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
      DataAccess.update(vis.sessionInfo());
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
CrawlerVis.prototype.initTagsGallery = function(predefinedTags, tagsLogic) {
  this.tagsGallery = new TagsGallery('#tags_items', predefinedTags, tagsLogic);
};


// Initializes pages gallery (snippets for selected pages).
CrawlerVis.prototype.initPagesGallery = function() {
  var vis = this;
  this.pagesGallery = new PagesGallery('#pages_items');
  this.pagesGallery.setCbIsTagRemovable(function(tag) {
    return vis.tagsGallery.isTagRemovable.call(vis.tagsGallery, tag);
  });
  this.pagesGallery.setCbGetExistingTags(function() {
    return vis.tagsGallery.getApplicableTags.call(vis.tagsGallery);
  });
};


// Load new pages when available at regular intervals
CrawlerVis.prototype.loadNewPagesSummary = function(isFilter) {
    var vis = this;
    DataAccess.loadNewPagesSummary(isFilter, vis.sessionInfo());
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
    var vis = this;
    DataAccess.loadTermSnippets(term, vis.sessionInfo());
  }
};


// Responds to toggle of a term.
// Term format:
// {'word': term, 'tags': [], ...}
CrawlerVis.prototype.onTermToggle = function(term, shiftClick) {
  var vis = this;

  if (shiftClick) {
    // Responds to shift click on a term: adds word to query list.
    var boxElem = d3.select('#query_box').node();
    boxElem.value += ' ' + term['word'];
  } else {
    // State machine: Neutral -> Positive -> Negative -> Neutral.
    var tags = term['tags'];

    if (tags.indexOf("Custom") != -1)
	return;

    var isPositive = tags.indexOf('Positive') != -1;
    var isNegative = tags.indexOf('Negative') != -1;

    if (isPositive) {
      // It was positive, so it turns negative.
      DataAccess.setTermTag(term['word'], 'Positive', false, vis.sessionInfo());
      DataAccess.setTermTag(term['word'], 'Negative', true, vis.sessionInfo());

      // Removes tag 'Positive' from tags array, adds 'Negative'.
      tags.splice(tags.indexOf('Positive'), 1);
      tags.push('Negative');
    }
    else if (isNegative) {
      // It was Negative, so it turns Neutral.
      DataAccess.setTermTag(term['word'], 'Negative', false, vis.sessionInfo());

      // Removes tag 'Negative' from tags array.
      tags.splice(tags.indexOf('Negative'), 1);
    }
    else {
      // It was Neutral, so it turns Negative.
      DataAccess.setTermTag(term['word'], 'Positive', true, vis.sessionInfo());

      // Adds tag 'Positive' to tags array.
      tags.push('Positive');
    }
    // Updates wordlist.
    vis.wordlist.update();

    // Triggers update of snippets to update its tags.
    __sig__.emit(__sig__.term_focus, term['word'], true);
  }
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

  var vis = this;
  // Fetches statistics for until last update happened.
  DataAccess.loadPagesSummaryUntilLastUpdate(false, vis.sessionInfo());
  DataAccess.loadPagesSummaryUntilLastUpdate(true, vis.sessionInfo());

  // Clears pages gallery.
  this.pagesGallery.clear();

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
  var applyTagFlag = action == 'Apply';
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
        tags.push(tag);
      } else {
        tags.splice(tags.indexOf(tag), 1);
      }
    }
  }
  
  var vis = this;
  if (urls.length > 0) {
    DataAccess.setPagesTag(urls, tag, applyTagFlag, vis.sessionInfo());
  }
  this.pagesLandscape.update();
  this.pagesGallery.update();
};


// Responds to clicked tag action for individual page.
CrawlerVis.prototype.onTagIndividualPageActionClicked = function(tag, action, item) {
  this.tagsGallery.applyOrRemoveTag(tag, action, [item]);
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
 * Initializes addc crawler button 
 */
CrawlerVis.prototype.initAddCrawlerButton = function() {
  d3.select('#submit_add_crawler').on('click', function() {
      var value = d3.select('#crawler_index_name').node().value;
      __sig__.emit(__sig__.add_crawler, value);

      // Hide domain modal after domain has been submitted.
      $("#addDomainModal").modal("hide");
    });
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


CrawlerVis.prototype.initAddTermButton = function() {
    d3.select('#add_term_button')
	.on('mouseover', function() {
	    Utils.showTooltip();
	})
	.on('mousemove', function() {
	    Utils.updateTooltip('Add custom relevant terms');
	})
	.on('mouseout', function() {
	    Utils.hideTooltip();
	})
	.on('click', function() {
	    var value = d3.select('#add_term_box').node().value;
	    __sig__.emit(__sig__.add_term, value);
	});
    d3.select('#add_term_neg_button')
	.on('mouseover', function() {
	    Utils.showTooltip();
	})
	.on('mousemove', function() {
	    Utils.updateTooltip('Add custom irrelevant terms');
	})
	.on('mouseout', function() {
	    Utils.hideTooltip();
	})
	.on('click', function() {
	    var value = d3.select('#add_term_box').node().value;
	    __sig__.emit(__sig__.add_neg_term, value);
	});

};


/**
 * Initializes filter button.
 */
CrawlerVis.prototype.initFilterButton = function() {
  var vis = this;
  d3.select('#submit_filter')
    .on('click', function() {
      var value = d3.select('#filter_box').node().value;
      __sig__.emit(__sig__.filter_enter, value);
    });
  // Initializes history of filters.
  this.filtersList = [];
};

/**
 * Initializes filter button.
 */
CrawlerVis.prototype.initModelButton = function() {
    var vis = this;
    d3.select('#build_model')
    .on('mouseover', function() {
      Utils.showTooltip();
    })
    .on('mousemove', function() {
      Utils.updateTooltip('Generate and download page classifier crawler model');
    })
    .on('mouseout', function() {
      Utils.hideTooltip();
    })

	.on('click', function() {
	    vis.createModelData();
	});
};

CrawlerVis.prototype.createModelData = function() {
    var vis = this;
    document.getElementById("status_panel").innerHTML = 'Building domain model...';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
    DataAccess.createModelData(vis.sessionInfo());
}

/**
 * Initializes calendar button.
 */
CrawlerVis.prototype.initFromCalendarButton = function() {
    var vis = this;
    $("#from_datetimepicker").datetimepicker({
	icons:{
	    time: "glyphicon glyphicon-time",
	    date: "glyphicon glyphicon-calendar"
	}
    });
};

/**
 * Initializes calendar button.
 */
CrawlerVis.prototype.initToCalendarButton = function() {    
    var vis = this;
    $('#to_datetimepicker').datetimepicker({
	icons:{
	    time: "glyphicon glyphicon-time",
	    date: "glyphicon glyphicon-calendar"
	}
    });
};

// Creates select to limit number of pages to load.
CrawlerVis.prototype.createSelectForFilterPageCap = function() {
  var vis = this;
  var selectBox = d3.select('#filter_cap_select');
  var getElementValue = function(d) {
    return d;
  };
  // Some options.
  var data = [10, 50, 100, 500, 1000, 2000];
  var options = selectBox.selectAll('option').data(data);
  options.enter().append('option');
  options
    .attr('value', getElementValue)
    .text(function(d, i) {
      return d;
    });

  $('#filter_cap_select').val(100);
};

/**
 * Applies query (useful for seed crawler vis).
 */
CrawlerVis.prototype.applyQuery = function(terms) {
  var vis = this;
  DataAccess.queryWeb(terms, vis.sessionInfo());
};

/**
 * Add crawler
 */
CrawlerVis.prototype.addCrawler = function(index_name) {
  DataAccess.addCrawler(index_name);
};


CrawlerVis.prototype.addTerm = function(term) {
    var vis = this;
    vis.wordlist.addEntries([{'word': term, 'posFreq': 0, 'negFreq': 0, 'tags': ["Positive", "Custom"]}]);
    
    DataAccess.setTermTag(term, 'Positive;Custom', true, vis.sessionInfo());
};

CrawlerVis.prototype.addNegTerm = function(term) {
    var vis = this;
    vis.wordlist.addEntries([{'word': term, 'posFreq': 0, 'negFreq': 0, 'tags': ["Negative", "Custom"]}]);
    DataAccess.setTermsTag(term, 'Negative;Custom', true, vis.sessionInfo());
};

CrawlerVis.prototype.deleteTerm = function(term) {
    var vis = this;
    DataAccess.deleteTerm(term, vis.sessionInfo());
};


/**
 * Runs query (useful for seed crawler vis).
 */
CrawlerVis.prototype.runQuery = function(terms) {
  this.applyQuery(terms);

  // Appends terms to history of queries.
  this.queriesList =
    this.appendToHistory('#query_box_previous_queries', this.queriesList, terms);
};

/**
 * Runs query (useful for seed crawler vis).
 */
CrawlerVis.prototype.runAddCrawler = function(index_name) {
    if (index_name === ""){
	document.getElementById("status_panel").innerHTML = 'Enter a valid domain name';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
  }
    else this.addCrawler(index_name);
};


/**
 * Run Add Term
 */

CrawlerVis.prototype.runAddTerm = function(term) {  
    if (term === ""){
	  document.getElementById("status_panel").innerHTML = 'Enter a valid term';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
    }
    else this.addTerm(term);
};

/**
 * Run Add Neg Term
 */

CrawlerVis.prototype.runAddNegTerm = function(term) {  
    if (term === ""){
	  document.getElementById("status_panel").innerHTML = 'Enter a valid term';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
}
    else this.addNegTerm(term);
};

/**
 * Run Delete Term
 */

CrawlerVis.prototype.runDeleteTerm = function(term) { 
    this.deleteTerm(term);
};

/**
 * Applies filter.
 */
CrawlerVis.prototype.applyFilter = function(terms) {
  var vis = this;  
  if (terms != undefined && terms != ""){
      document.getElementById("status_panel").innerHTML = 'Applying filter...';
    $(document).ready(function() { $(".status_box").fadeIn(); });
    $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      // Applies filter and issues an update automatically.
      DataAccess.update(vis.sessionInfo());
  }
};

/**
 * Runs filter.
 */
CrawlerVis.prototype.runFilter = function(terms) {
  this.applyFilter(terms);

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

// Return all the session info
CrawlerVis.prototype.sessionInfo = function() {
    var algId = d3.select('#selectProjectionAlgorithm').node().value;
    var domainId = d3.select('input[name="crawlerRadio"]:checked').node().value;
    var cap = d3.select('#filter_cap_select').node().value;
    
    var fromdate_local = new Date(d3.select('#fromdate').node().value);
    var todate_local = new Date(d3.select('#todate').node().value);
    
    if (fromdate_local != "Invalid Date")
	var fromdate_utc = Utils.toUTC(fromdate_local);
    else fromdate_utc = null;
    if (todate_local != "Invalid Date")
	var todate_utc = Utils.toUTC(todate_local);
    else todate_utc = null;
    
    var filterTerms = d3.select('#filter_box').node().value;
    if (filterTerms === '')
	filterTerms = null;
    return {
	domainId: domainId,
	activeProjectionAlg: algId,
	pagesCap: cap,
	filter: filterTerms, 
	fromDate: fromdate_utc,
	toDate: todate_utc
    };
};

$(document).ready(function() {
$(".panel-heading").click(function () {
    $header = $(this);
    //getting the next element
    $content = $header.next();
    //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
    $content.slideToggle(400, function(){
        if( $content.is(":visible")){
        $header.find("span.collapsethis").removeClass("glyphicon-plus");
        $header.find("span.collapsethis").addClass("glyphicon-minus");        
  }
  else{
        $header.find("span.collapsethis").removeClass("glyphicon-minus");
        $header.find("span.collapsethis").addClass("glyphicon-plus");
    }
    });
    
    
});
});
