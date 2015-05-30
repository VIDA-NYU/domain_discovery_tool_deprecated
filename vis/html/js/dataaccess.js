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
  };

  // Processes loaded terms summaries.
  var onTermsSummaryLoaded = function(summary) {
    termsSummary = summary;
    loadingTerms = false;
  };

  // Processes loaded pages and terms.
  var onMaybeUpdateComplete = function() {
    updating = loadingPages || loadingTerms;
    if (!updating) {
      __sig__.emit(__sig__.pages_loaded, pages);
      __sig__.emit(__sig__.terms_summary_fetched, termsSummary);
    }
  };

  // Processes loaded list of available crawlers.
  var onAvailableCrawlersLoaded = function(crawlers) {
    __sig__.emit(__sig__.available_crawlers_list_loaded, crawlers);
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
  // Sets current crawler Id.
  pub.setActiveCrawler = function(crawlerId) {
    currentCrawler = crawlerId;
    runQuery('/setActiveCrawler', {'crawlerId': crawlerId});
  };
  // Queries the web for terms (used in Seed Crawler mode).
  pub.queryWeb = function(terms) {
    runQueryForCurrentCrawler('/queryWeb', {'terms': terms});
  };
  // Applies filter to returned pages and pages result.
  pub.applyFilter = function(terms) {
    runQueryForCurrentCrawler('/applyFilter', {'terms': terms});
  };
  // Loads pages (complete data, including URL, x and y position etc) and terms.
  pub.update = function() {
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
