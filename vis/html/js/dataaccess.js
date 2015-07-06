/**
 * Manages clock used to fetch pages summaries, and exposes access to back end.
 *
 * May 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */
var DataAccess = (function() {
  var pub = {};

  var REFRESH_EVERY_N_MILLISECONDS = 2000;

  var lastUpdate = 0;
  var lastSummary = 0;
  var currentCrawler = undefined;
  var currentProjAlg = undefined;
  var loadingSummary = false;
  var updating = false;
  var loadingPages = false;
  var loadingTerms = false;
  var pages = undefined;
  var termsSummary = undefined;

  // Processes loaded pages summaries.
  var onPagesSummaryUntilLastUpdateLoaded = function(summary, isFilter) {
    __sig__.emit(__sig__.previous_pages_summary_fetched, summary, isFilter);
  };

  // Processes loaded pages summaries.
  var onNewPagesSummaryLoaded = function(summary, isFilter) {
    loadingSummary = false;
    lastSummary = moment().unix();
    __sig__.emit(__sig__.new_pages_summary_fetched, summary, isFilter);
  };

  // Processes loaded pages.
  var onPagesLoaded = function(loadedPages) {
      pages = loadedPages;
      lastUpdate = loadedPages['last_downloaded_url_epoch'];
      loadingPages = false;
      document.getElementById("status_panel").innerHTML = 'Processing pages...Done';
  };

  // Processes loaded terms summaries.
  var onTermsSummaryLoaded = function(summary) {
      termsSummary = summary;
      loadingTerms = false;
      document.getElementById("status_panel").innerHTML = 'Processing terms...Done';
  };

  // Processes loaded pages and terms.
  var onMaybeUpdateComplete = function() {
    updating = loadingPages || loadingTerms;
    if (!updating) {
	__sig__.emit(__sig__.pages_loaded, pages);
	__sig__.emit(__sig__.terms_summary_fetched, termsSummary);

	if (pages['pages'].length == 0)
	    document.getElementById("status_panel").innerHTML = 'No pages found';

	Utils.setWaitCursorEnabled(false);
    }
  };

  // Processes loaded list of available crawlers.
  var onAvailableCrawlersLoaded = function(crawlers) {
    __sig__.emit(__sig__.available_crawlers_list_loaded, crawlers);
  };

  // Reloads list of available crawlers.
  var onAvailableCrawlersReLoaded = function(crawlers) {
    __sig__.emit(__sig__.available_crawlers_list_reloaded, crawlers);
  };

  // Reloads the select crawlers when the new crawler is added
  var onCrawlerAdded = function(){
      pub.reloadAvailableCrawlers()
  }

  // Called when queryweb is done
  var onQueryWebDone = function() {
      Utils.setWaitCursorEnabled(false);
      document.getElementById("status_panel").innerHTML = 'Downloading pages...see page summary for real-time page download status';
  };
 
  // Processes loaded list of available projection algorithms.
  var onAvailableProjAlgLoaded = function(proj_alg) {
    __sig__.emit(__sig__.available_proj_alg_list_loaded, proj_alg);
  };

  // Processes loaded term snippets.
  var onLoadedTermsSnippets = function(snippetsData) {
    __sig__.emit(__sig__.terms_snippets_loaded, snippetsData);
  };

  // Runs async post query.
  var runQuery = function(query, args, onCompletion, doneCb) {
    $.post(
      query,
      args,
      onCompletion)
    .done(doneCb);
  };

  // Runs async post query for current crawler.
  var runQueryForCurrentCrawler = function(query, args, onCompletion, doneCb) {
    if (currentCrawler !== undefined) {
      runQuery(query, args, onCompletion, doneCb);
    }
  };

  // Runs async post query for current crawler.
  var runQueryForCurrentProjAlg = function(query, args, onCompletion, doneCb) {
    if (currentProjAlg !== undefined) {
      runQuery(query, args, onCompletion, doneCb);
    }
  };

  // TODO(cesar): Load both terms and pages summaries, and update after both complete.
  //queue()
  //  .defer(loadNewPagesSummary)
  //  .awaitAll(function(results) {
  //    onPagesSummaryLoaded(results[0]);
  //    console.log(results);
  //  });

  // Loads new pages summary.
  pub.loadNewPagesSummary = function(isFilter) {
    if (!loadingSummary && currentCrawler !== undefined) {
      loadingSummary = true;
      runQueryForCurrentCrawler(
        '/getPagesSummary', {'opt_ts1': lastUpdate},
        function(summary) {
          onNewPagesSummaryLoaded(summary, isFilter);
        });
    }
  };
  // Loads pages summary until last pages update.
  pub.loadPagesSummaryUntilLastUpdate = function(isFilter) {
    if (currentCrawler !== undefined) {
      runQueryForCurrentCrawler(
        '/getPagesSummary', {'opt_ts2': lastUpdate, 'opt_applyFilter': isFilter},
        function(summary) {
          onPagesSummaryUntilLastUpdateLoaded(summary, isFilter);
        });
    }
  };
  // Returns public interface.
  // Gets available crawlers from backend.
  pub.loadAvailableCrawlers = function() {
    runQuery('/getAvailableCrawlers', {}, onAvailableCrawlersLoaded);
  };

  // Returns public interface.
  // Gets available crawlers from backend.
  pub.reloadAvailableCrawlers = function() {
    runQuery('/getAvailableCrawlers', {}, onAvailableCrawlersReLoaded);
  };

  // Sets current crawler Id.
  pub.setActiveCrawler = function(crawlerId) {
    currentCrawler = crawlerId;
    runQuery('/setActiveCrawler', {'crawlerId': crawlerId});
  };
  // Returns public interface.
  // Gets available crawlers from backend.
  pub.loadAvailableProjectionAlgorithms = function() {
    runQuery('/getAvailableProjectionAlgorithms', {}, onAvailableProjAlgLoaded);
  };
  // Sets current crawler Id.
  pub.setActiveProjectionAlg = function(algId) {
    currentProjAlg = algId;
    runQuery('/setActiveProjectionAlg', {'algId': algId});
  };
  // Queries the web for terms (used in Seed Crawler mode).
  pub.queryWeb = function(terms) {
      Utils.setWaitCursorEnabled(true);
      document.getElementById("status_panel").innerHTML = 'Querying the Web...';
      runQueryForCurrentCrawler('/queryWeb', {'terms': terms}, onQueryWebDone);
  };

  // Add new crawler
  pub.addCrawler = function(index_name) {
      document.getElementById("status_panel").innerHTML = 'Adding new crawler - ' + index_name;
      runQueryForCurrentCrawler('/addCrawler', {'index_name': index_name}, onCrawlerAdded);
  }

  // Applies filter to returned pages and pages result.
  pub.applyFilter = function(terms) {
    runQueryForCurrentCrawler('/applyFilter', {'terms': terms});
  };
  // Loads pages (complete data, including URL, x and y position etc) and terms.
  pub.update = function() {
    Utils.setWaitCursorEnabled(true);

      document.getElementById("status_panel").innerHTML = 'Processing pages and terms...';
   
      
    if (!updating && currentCrawler !== undefined) {
      updating = true;

      // Fetches pages summaries every n seconds.
      loadingPages = true;
      runQueryForCurrentCrawler(
        '/getPages', {}, onPagesLoaded, onMaybeUpdateComplete);

      // Fetches terms summaries.
      loadingTerms = true;
      runQueryForCurrentCrawler(
        '/getTermsSummary', {}, onTermsSummaryLoaded, onMaybeUpdateComplete);
    }
  };
  // Loads snippets for a given term.
  pub.loadTermSnippets = function(term) {
    runQueryForCurrentCrawler('/getTermSnippets', {'term': term}, onLoadedTermsSnippets);
  };
  // Boosts pages given by url.
  pub.boostPages = function(pages) {
    runQueryForCurrentCrawler('/boostPages', {'pages': pages.join('|')});
  };
  // Accesses last update time in Unix epoch time.
  pub.getLastUpdateTime = function() {
    return lastUpdate;
  };
  // Accesses last summary loading time in Unix epoch time.
  pub.getLastSummaryTime = function() {
    return lastSummary;
  };
  // Adds tag to page.
  pub.setPageTag = function(page, tag, applyTagFlag) {
    runQueryForCurrentCrawler(
      '/setPagesTag', {'pages': page, 'tag': tag, 'applyTagFlag': applyTagFlag});
  };
  // Adds tag to multiple pages.
  pub.setPagesTag = function(pages, tag, applyTagFlag) {
    if (pages.length > 0) {
      runQueryForCurrentCrawler(
        '/setPagesTag', {'pages': pages.join('|'), 'tag': tag, 'applyTagFlag': applyTagFlag});
    }
  };
  // Adds tag to term.
  pub.setTermTag = function(term, tag, applyTagFlag) {
    runQueryForCurrentCrawler(
      '/setTermsTag', {'terms': term, 'tag': tag, 'applyTagFlag': applyTagFlag});
  };
  // Sets limit of number of pages loaded.
  pub.setPagesCountCap = function(cap) {
    runQueryForCurrentCrawler(
      '/setPagesCountCap', {'pagesCap': cap});
  };

  // Fetches new pages summaries every n seconds.
  window.setInterval(function() {pub.loadNewPagesSummary(false);}, REFRESH_EVERY_N_MILLISECONDS);
  window.setInterval(function() {pub.loadNewPagesSummary(true);}, REFRESH_EVERY_N_MILLISECONDS);

  return pub;
}());
