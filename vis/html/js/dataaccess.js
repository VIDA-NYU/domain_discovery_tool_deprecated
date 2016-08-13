/**
 * Manages clock used to fetch pages summaries, and exposes access to back end.
 *
 * May 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */
 var trailx = d3.select("#containerSequence").append("svg")
     .attr("id", "trail")
     .attr({
     width: 0,
     height: 0
 });

var DataAccess = (function() {
  var pub = {};

    var REFRESH_EVERY_N_MILLISECONDS = 2000;

  var lastUpdate = 0;
  var lastSummary = 0;
  var currentCrawler = undefined;
  var currentProjAlg = undefined;
  var loadingSummary = false;
  var updatingClassifier = false;
  var updating = false;
  var loadingPages = false;
  var loadingTerms = false;
  var pages = undefined;
  var termsSummary = undefined;
  var lastAccuracy = undefined;  

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

  // Triggers page summary update after the pages are tagged
  var onSetPagesTagCompleted = function(){
      __sig__.emit(__sig__.set_pages_tags_completed);
  }

    var onUpdatedOnlineClassifier = function(accuracy){
	updatingClassifier = false;
	lastAccuracy = accuracy;
      __sig__.emit(__sig__.update_online_classifier_completed, accuracy);
  }
  // Processes loaded pages.
  var onPagesLoaded = function(loadedPages) {
      pages = loadedPages;
      loadingPages = false;
      if(pages["data"]["pages"].length > 0){
	  lastUpdate = moment().unix();
	  document.getElementById("status_panel").innerHTML = 'Processing pages...Done';
	  $(document).ready(function() { $(".status_box").fadeIn(); });
	  $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      }
  };

  // Processes loaded terms summaries.
  var onTermsSummaryLoaded = function(summary) {
      termsSummary = summary;
      loadingTerms = false;
      if(termsSummary.length > 0){
	  document.getElementById("status_panel").innerHTML = 'Processing terms...Done';
	  $(document).ready(function() { $(".status_box").fadeIn(); });
	  $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      }
  };

  // Processes loaded pages.
    var onMaybeUpdateCompletePages = function() {
	updating = loadingPages || loadingTerms;

	// Update status of the update button
	d3.select('#pages_landscape_update')
	    .classed('enabled', !updating)
	    .classed('disabled', updating)

	if (!loadingPages) {
	    if (pages["data"]["pages"].length === 0){
		document.getElementById("status_panel").innerHTML = 'No pages found';
		$(document).ready(function() { $(".status_box").fadeIn(); });
		$(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
		__sig__.emit(__sig__.pages_loaded, pages["data"]);
	    } else {
		__sig__.emit(__sig__.pages_loaded, pages["data"]);
		__sig__.emit(__sig__.bokeh_insert_plot, pages);
	    }
	    Utils.setWaitCursorEnabled(false);
	}
    };

    // Processes loaded terms.
    var onMaybeUpdateCompleteTerms = function() {
	updating = loadingPages || loadingTerms;

	// Update status of the update button
	d3.select('#pages_landscape_update')
	    .classed('enabled', !updating)
	    .classed('disabled', updating)

	if (!loadingTerms) {
	    if(termsSummary.length > 0){
      		__sig__.emit(__sig__.terms_summary_fetched, termsSummary);
	    }
	}
    }

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
    __sig__.emit(__sig__.available_crawlers_list_loaded, crawlers["crawlers"]);
  };

  // Reloads list of available crawlers.
    var onAvailableCrawlersReLoaded = function(result) {
    __sig__.emit(__sig__.available_crawlers_list_reloaded, result);
  };

  // Reloads the select crawlers when the new crawler is added
  var onCrawlerAdded = function(){
      pub.reloadAvailableCrawlers("add")
  }

  var onCrawlerDeleted = function(){
      pub.reloadAvailableCrawlers("delete")
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

  // Processes loaded tag color mapping
  var onAvailableTagColorsLoaded = function(tagColors){
      __sig__.emit(__sig__.tags_colors_loaded, tagColors);
  };

  //Signal load of new pages after certain interval
  var loadNewPagesSummary = function(isFilter) {
      __sig__.emit(__sig__.load_new_pages_summary, isFilter);
  };


  //Signal update of online classifier
  var updateOnlineClassifier = function() {
      __sig__.emit(__sig__.update_online_classifier);
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
    if (currentCrawler !== undefined || query === "/addCrawler" || query === "/delCrawler") {
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
      runQuery('/getAvailableCrawlers', {"type": "init"}, onAvailableCrawlersLoaded);
  };

  // Returns public interface.
  // Gets available crawlers from backend.
  pub.reloadAvailableCrawlers = function(type) {
      runQuery('/getAvailableCrawlers', {"type": type}, onAvailableCrawlersReLoaded);
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
    //alert("query en queries: " + JSON.stringify(session) + ", querieload: "+ onAvailableQueriesLoaded);
      runQuery('/getAvailableQueries', {'session': JSON.stringify(session)}, onAvailableQueriesLoaded);
  };

  // Returns public interface.
  // Gets available tags from backend.
    pub.loadAvailableTags = function(session, event) {
      //alert("alert query para tags: " + JSON.stringify(session) + ", tagload: " + onAvailableTagsLoaded);
	runQuery('/getAvailableTags', {'session': JSON.stringify(session), 'event': event}, onAvailableTagsLoaded);
  };

  // Returns public interface.
  // Gets available tag color mapping from backend.
    pub.loadTagColors = function(crawlerId) {
      runQuery('/getTagColors', {'domainId': crawlerId}, onAvailableTagColorsLoaded);
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

  // Add new crawler
  pub.delCrawler = function(domains) {
      document.getElementById("status_panel").innerHTML = 'Deleting crawler';
      $(document).ready(function() { $(".status_box").fadeIn(); });
      $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
      runQueryForCurrentCrawler('/delCrawler', {'domains': JSON.stringify(domains)}, onCrawlerDeleted);
  }

  // Loads pages (complete data, including URL, x and y position etc) and terms.
  pub.update = function(session) {

      if (!updating && currentCrawler !== undefined) {

	  Utils.setWaitCursorEnabled(true);

	  document.getElementById("status_panel").innerHTML = 'Processing pages and terms...';
	  $(document).ready(function() { $(".status_box").fadeIn(); });
	  $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));

	  // Update status of the update button
	  d3.select('#pages_landscape_update')
	      .classed('enabled', false)
	      .classed('disabled', true);

	  updating = true;

	  // Fetches pages summaries every n seconds.
	  loadingPages = true;
	  runQueryForCurrentCrawler(
              '/getPages', {'session': JSON.stringify(session)}, onPagesLoaded, onMaybeUpdateCompletePages);
              //alert("consultaQueries: " + JSON.stringify(session) + ", onpagesload: "+  onPagesLoaded +", onMaybeUpdateCompletePages: "+ onMaybeUpdateCompletePages);
              //create top bar wich shows the applied filters.
              var obj = JSON.parse(JSON.stringify(session));
              var newobj = buildHierarchy(obj);
              GetCheckedStateNew(newobj);

	  // Fetches terms summaries.
	  loadingTerms = true;
	  runQueryForCurrentCrawler(
              '/getTermsSummary', {'session': JSON.stringify(session)}, onTermsSummaryLoaded, onMaybeUpdateCompleteTerms);

	  runQueryForCurrentCrawler(
	      '/updateOnlineClassifier', {'session': JSON.stringify(session)}, onUpdatedOnlineClassifier);
      }
  };

  pub.crawlPages = function(urls, crawl_type, session){
      if(crawl_type === "forward"){
	  document.getElementById("status_panel").innerHTML = 'Querying forward links in selected pages...see page summary for real-time page download status';
	  $(document).ready(function() { $(".status_box").fadeIn(); });
	  $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
	  runQueryForCurrentCrawler('/getForwardLinks', {'urls': urls.join('|'), 'session': JSON.stringify(session)});
      }
      else if(crawl_type === "backward"){
	  document.getElementById("status_panel").innerHTML = 'Querying back links of selected pages...see page summary for real-time page download status';
	  $(document).ready(function() { $(".status_box").fadeIn(); });
	  $(document).ready(setTimeout(function() {$('.status_box').fadeOut('fast');}, 5000));
	  runQueryForCurrentCrawler('/getBackwardLinks', {'urls': urls.join('|'), 'session': JSON.stringify(session)});
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

  // Accesses last accuracy reported
  pub.getLastAccuracy = function() {
    return lastAccuracy;
  };

  // Accesses last accuracy reported
  pub.setLastAccuracy = function(accuracy) {
    lastAccuracy = accuracy;
  };

  // Accesses last summary loading time in Unix epoch time.
  pub.getLastSummaryTime = function() {
    return lastSummary;
  };
  // Adds tag to multiple pages.
  pub.setPagesTag = function(pages, tag, applyTagFlag, session) {
    if (pages.length > 0) {
      runQueryForCurrentCrawler(
          '/setPagesTag', {'pages': pages.join('|'), 'tag': tag, 'applyTagFlag': applyTagFlag, 'session': JSON.stringify(session)}, onSetPagesTagCompleted);
    }
  };
  // Adds tag to term.
  pub.setTermTag = function(term, tag, applyTagFlag, session) {
    runQueryForCurrentCrawler(
      '/setTermsTag', {'terms': term, 'tag': tag, 'applyTagFlag': applyTagFlag, 'session': JSON.stringify(session)});
  };

  //Update online classifier
  pub.updateOnlineClassifier = function(session) {
      if (!updatingClassifier && currentCrawler !== undefined) {
	  updatingClassifier = true;
	  runQueryForCurrentCrawler(
	      '/updateOnlineClassifier', {'session': JSON.stringify(session)}, onUpdatedOnlineClassifier);
      }
  }

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
  };

  // Update tag color mapping
  pub.updateColors = function(session, colors){
      runQueryForCurrentCrawler(
	  '/updateColors', {'session': JSON.stringify(session), 'colors': JSON.stringify(colors)});
  };

  // Fetches new pages summaries every n seconds.
  window.setInterval(function() {loadNewPagesSummary(false);}, REFRESH_EVERY_N_MILLISECONDS);
  window.setInterval(function() {loadNewPagesSummary(true);}, REFRESH_EVERY_N_MILLISECONDS);
 //window.setInterval(function() {updateOnlineClassifier();}, REFRESH_EVERY_N_MILLISECONDS + 18000);

  return pub;
}());

//Take a query 'JSON.stringify(session)' for create an array with json objects.
//Which contains the filters's sequence even queries and tags.
function buildHierarchy(value) {
    var path = [];
    path.length = 0;
    //var root = {"name": "root", "children": []};
    var lengthFilter =0;
    if(value.filter!=null){
      var selectedFilter = value.filter; var typeName = "Filter";
      lengthFilter =typeName.length + selectedFilter.length;
      var childNode = {"name": selectedFilter, "type": typeName, "length": lengthFilter};
      path.unshift(childNode);
    }
    if((typeof value.selected_queries=="undefined")&& (typeof value.selected_tags=="undefined")&& (typeof value.selected_tags=="undefined")) { //if(value.pageRetrievalCriteria=="Most Recent" && value.selected_queries=="" && value.selected_tags==""){
      var selectedFilter = value.pageRetrievalCriteria;
      var childNode = {"name": "Most Recent", "type": "Most Recent", "length": lengthFilter};
      path.unshift(childNode);
    }
    if(value.selected_morelike!=""){ //if(value.selected_morelike!="More like"){
      var selectedMoreLike = value.selected_morelike;
      var childNode = {"name": selectedMoreLike, "type": "MoreLike", "length": (value.pageRetrievalCriteria).length +selectedMoreLike.length+lengthFilter};
      path.unshift(childNode);
    }
    if (value.selected_tags!="" && !(typeof value.selected_tags=="undefined")) { // if (value.pageRetrievalCriteria=="Tags") {
      var selectedTags = value.selected_tags;
      var childNode = {"name": selectedTags, "type": "Tags", "length": (value.pageRetrievalCriteria).length +selectedTags.length + lengthFilter};
      path.unshift(childNode);
    }
    if (value.selected_queries!="" && !(typeof value.selected_queries=="undefined")) { //if (value.pageRetrievalCriteria=="Queries") {
      var selectedQueries = value.selected_queries;
      var childNode = {"name": selectedQueries, "type": "Queries", "length": (value.pageRetrievalCriteria).length + selectedQueries.length + lengthFilter}; //var childNode = {"name": selectedQueries, "type": value.pageRetrievalCriteria, "length": (value.pageRetrievalCriteria).length + selectedQueries.length + lengthFilter};
      path.unshift(childNode);
    }
    return path;
  }

var nroNames =0;
// Create/update the container which shows current sequence of applied filters (these appear as buttons).
  function GetCheckedStateNew( newobj) {
      var list_buttons="<div class='row' style='margin-left:1px; margin-right:5px;'>";

      var g = d3.select("#trail")
      .selectAll("g")
      .data(newobj, function(d) { return d.name;});
        // Add breadcrumb and label for entering nodes.
        var entering = g.enter().append("svg:g");
        g.append("foreignObject")
        .attr("x", function(d) { return 0; })
        .attr("y", 0)
        .append("xhtml")
        .html(function(d) {
            var filters = (d.name).split(",");
            if(filters[0]==""){
              return "";
            }
            else{
              var typeFilter = d.type;
              var buttons= "<div style='float: left; background-color:#ccadc7; padding: 2px 2px 2px 2px;margin-bottom:2px;margin-right:2px;'>" + typeFilter + ": ";
              var nameButton = typeFilter+"_";
              for(var i=0; i<filters.length ; i++){
                if(filters[i] !="select_all")
                buttons = buttons + " <button id='"+nameButton+i +"' class='btn btn-default btn-xs' onclick='removeButton(\"" + nameButton+i+","+filters[i] + "\")'>"+ filters[i]+"</button>";
              }
              buttons = buttons + "</div>"
              list_buttons= list_buttons + buttons;
              return ""; //buttons;
            }
        } );
        list_buttons =list_buttons + "</div>";
          g.exit().remove();
            document.getElementById("list_buttons_div").innerHTML = list_buttons;
}

//Remove the selected button and descheck the associated checkbox.
function removeButton(infoButton) {
  var info = infoButton.split(",");
  if(info[0].indexOf("Filter") > -1){
    var filterInfo = d3.select('#filter_box').node().value;
    d3.select('#filter_box').node().value = "";
  }else{
    if(info[0].indexOf("MoreLike") > -1){
      checkboxes = document.getElementsByName('morelike_checkbox');
    }
    if(info[0].indexOf("Queries") > -1){
      checkboxes = document.getElementsByName('queries_checkbox');
    }
    if(info[0].indexOf("Tags") > -1){
      checkboxes = document.getElementsByName('tags_checkbox');
    }
    for (var checkbox in checkboxes){
      if(checkboxes[checkbox].value == info[1]){
      checkboxes[checkbox].checked = this.checked;}
    }
 }
  var nameButton="#" + info[0];
  $(nameButton).remove();
}
