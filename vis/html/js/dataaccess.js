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
      lastUpdate = loadedPages["data"]['last_downloaded_url_epoch'];
      loadingPages = false;
      document.getElementById("status_panel").innerHTML = 'Processing pages...Done';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
  };

  // Processes loaded terms summaries.
  var onTermsSummaryLoaded = function(summary) {
      termsSummary = summary;
      loadingTerms = false;
      document.getElementById("status_panel").innerHTML = 'Processing terms...Done';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
  };

  // Processes loaded pages and terms.
    var onMaybeUpdateComplete = function() {
	updating = loadingPages || loadingTerms;
	if (!loadingPages && loadingTerms) {
	    __sig__.emit(__sig__.pages_loaded, pages["data"]);
	    __sig__.emit(__sig__.bokeh_insert_plot, pages);
	    
	    if (pages["data"].length === 0){
		document.getElementById("status_panel").innerHTML = 'No pages found';
		$(document).ready(function() { $(".status_box").fadeIn(); });
		$(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
	    }
	    Utils.setWaitCursorEnabled(false);
	}
	
	if (!loadingTerms) {
      	    __sig__.emit(__sig__.terms_summary_fetched, termsSummary);
	}
    };

 // Signals model creation completion
 var onModelCreated = function(model_file) {
     Utils.setWaitCursorEnabled(false);
     document.getElementById("status_panel").innerHTML = 'Building crawler model...Done';
     $(document).ready(function() { $(".status_box").fadeIn(); });
     $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
     var url = model_file;    
     window.open(url,'Download');  
 }

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

  // Processes loaded list of available projection algorithms.
  var onAvailableProjAlgLoaded = function(proj_alg) {
    __sig__.emit(__sig__.available_proj_alg_list_loaded, proj_alg);
  };

  // Processes loaded term snippets.
  var onLoadedTermsSnippets = function(snippetsData) {
    __sig__.emit(__sig__.terms_snippets_loaded, snippetsData);
  };

  // Processes loaded queries
  var onAvailableQueriesLoaded = function(queriesData) {
    __sig__.emit(__sig__.queries_loaded, queriesData);
  };

  // Processes loaded tags
  var onAvailableTagsLoaded = function(tagsData) {
    __sig__.emit(__sig__.tags_loaded, tagsData);
  };


  //Signal load of new pages after certain interval
  var loadNewPagesSummary = function(isFilter) {
      __sig__.emit(__sig__.load_new_pages_summary, isFilter);
      __sig__.emit(__sig__.bokeh_get_session);
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
    if (currentCrawler !== undefined || query === "/addCrawler") {
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
  pub.loadNewPagesSummary = function(isFilter, session) {
    if (!loadingSummary && currentCrawler !== undefined) {
      loadingSummary = true;
      runQueryForCurrentCrawler(
        '/getPagesSummary', {'opt_ts1': lastUpdate, 'session': JSON.stringify(session)},
        function(summary) {
          onNewPagesSummaryLoaded(summary, isFilter);
        });
    }
  };
  // Loads pages summary until last pages update.
  pub.loadPagesSummaryUntilLastUpdate = function(isFilter, session) {
    //if (currentCrawler !== undefined) {
      runQueryForCurrentCrawler(
        '/getPagesSummary', {'opt_ts2': lastUpdate, 'opt_applyFilter': isFilter, 'session': JSON.stringify(session)},
        function(summary) {
          onPagesSummaryUntilLastUpdateLoaded(summary, isFilter);
        });
    //}
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
  };

  // Returns public interface.
  // Gets available projection algorithms.
  pub.loadAvailableProjectionAlgorithms = function() {
    runQuery('/getAvailableProjectionAlgorithms', {}, onAvailableProjAlgLoaded);
  };

  // Sets current crawler Id.
  pub.setActiveProjectionAlg = function(algId) {
    currentProjAlg = algId;
  };

  // Returns public interface.
  // Gets available queries from backend.
  pub.loadAvailableQueries = function(session) {
      runQuery('/getAvailableQueries', {'session': JSON.stringify(session)}, onAvailableQueriesLoaded);
  };

  // Returns public interface.
  // Gets available tags from backend.
  pub.loadAvailableTags = function(session) {
      runQuery('/getAvailableTags', {'session': JSON.stringify(session)}, onAvailableTagsLoaded);
  };
  
  // Queries the web for terms (used in Seed Crawler mode).
  pub.queryWeb = function(terms, session) {
      document.getElementById("status_panel").innerHTML = 'Querying the Web...see page summary for real-time page download status';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      runQueryForCurrentCrawler('/queryWeb', {'terms': terms, 'session': JSON.stringify(session)});
  };

  // Downloads the pages of given urls
  pub.downloadUrls = function(urls, session) {
      document.getElementById("status_panel").innerHTML = 'Downloading uploaded URLs...see page summary for real-time page download status';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      runQueryForCurrentCrawler('/downloadUrls', {'urls': urls, 'session': JSON.stringify(session)});
  };

  // Add new crawler
  pub.addCrawler = function(index_name) {
      document.getElementById("status_panel").innerHTML = 'Adding new crawler - ' + index_name;
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      runQueryForCurrentCrawler('/addCrawler', {'index_name': index_name}, onCrawlerAdded);
  }

  // Loads pages (complete data, including URL, x and y position etc) and terms.
  pub.update = function(session) {
      Utils.setWaitCursorEnabled(true);
      
      document.getElementById("status_panel").innerHTML = 'Processing pages and terms...';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));

    if (!updating && currentCrawler !== undefined) {
      updating = true;

      // Fetches pages summaries every n seconds.
      loadingPages = true;
      runQueryForCurrentCrawler(
        '/getPages', {'session': JSON.stringify(session)}, onPagesLoaded, onMaybeUpdateComplete);

      // Fetches terms summaries.
      loadingTerms = true;
      runQueryForCurrentCrawler(
        '/getTermsSummary', {'session': JSON.stringify(session)}, onTermsSummaryLoaded, onMaybeUpdateComplete);
    }
  };
  // Loads snippets for a given term.
  pub.loadTermSnippets = function(term, session) {
    runQueryForCurrentCrawler('/getTermSnippets', {'term': term, 'session': JSON.stringify(session)}, onLoadedTermsSnippets);
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
  // Adds tag to multiple pages.
  pub.setPagesTag = function(pages, tag, applyTagFlag, session) {
    if (pages.length > 0) {
      runQueryForCurrentCrawler(
        '/setPagesTag', {'pages': pages.join('|'), 'tag': tag, 'applyTagFlag': applyTagFlag, 'session': JSON.stringify(session)});
    }
  };
  // Adds tag to term.
  pub.setTermTag = function(term, tag, applyTagFlag, session) {
    runQueryForCurrentCrawler(
      '/setTermsTag', {'terms': term, 'tag': tag, 'applyTagFlag': applyTagFlag, 'session': JSON.stringify(session)});
  };

    
  pub.deleteTerm = function(term, session) {
      runQueryForCurrentCrawler('/deleteTerm', {'term': term, 'session': JSON.stringify(session)});
  }

  // Sets limit of number of pages loaded.
  pub.setPagesCountCap = function(cap) {
    runQueryForCurrentCrawler(
      '/setPagesCountCap', {'pagesCap': cap});
  };

  // Set the time range for filtering pages retrieved 
  pub.setDateTime = function(fromdate, todate){
      runQueryForCurrentCrawler(
	  '/setDateTime', {'fromDate': fromdate, 'toDate': todate});
  };

  // Generate data to build crawler model
  pub.createModelData = function(session){
      Utils.setWaitCursorEnabled(true);
      runQueryForCurrentCrawler(
	  '/createModel', {'session': JSON.stringify(session)}, onModelCreated);
  }
  // Fetches new pages summaries every n seconds.
  window.setInterval(function() {loadNewPagesSummary(false);}, REFRESH_EVERY_N_MILLISECONDS);
  window.setInterval(function() {loadNewPagesSummary(true);}, REFRESH_EVERY_N_MILLISECONDS);

  return pub;
}());
