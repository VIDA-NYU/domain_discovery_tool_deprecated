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
  var lastSummary = undefined;
  var currentCrawler = undefined;
  var loadingSummary = false;
  var updating = false;
  var loadingPages = false;
  var loadingTerms = false;
  var pages = undefined;
  var termsSummary = undefined;

  // Processes loaded pages summaries.
  var onPagesSummaryLoaded = function(summary) {
    loadingSummary = false;
    lastSummary = moment().unix();
    __sig__.emit(__sig__.new_pages_summary_fetched, summary);
  };

  // Processes loaded pages.
  var onPagesLoaded = function(loadedPages) {
    pages = loadedPages;
    lastUpdate = moment().unix();
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
  //  .defer(loadPagesSummary)
  //  .awaitAll(function(results) {
  //    onPagesSummaryLoaded(results[0]);
  //    console.log(results);
  //  });

  window.setInterval(function() {
    if (!loadingSummary && currentCrawler !== undefined) {
      loadingSummary = true;

      // Fetches pages summaries every n seconds.
      loadingPages = true;
      runQueryForCurrentCrawler(
        '/getPagesSummary', {'opt_ts1': lastUpdate}, onPagesSummaryLoaded);
    }
  }, REFRESH_EVERY_N_MILLISECONDS);


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
  // Loads pages (complete data, including URL, x and y position etc) and terms.
  pub.update = function() {
    if (!updating && currentCrawler !== undefined) {
      updating = true;

      // Fetches pages summaries every n seconds.
      loadingPages = true;
      runQueryForCurrentCrawler(
        '/getPages', {'opt_ts1': lastUpdate}, onPagesLoaded, onMaybeUpdateComplete);

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
  return pub;
}());
