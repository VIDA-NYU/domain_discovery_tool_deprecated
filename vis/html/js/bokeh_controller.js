/**
 * This module handles communication between the bokeh callbacks and the rest of
 * the DDT application. Many of these functions are helper functions called from
 * the bokeh CustomJS callbacks in `vis/bokeh_graphs/clustering.py`.
 */
(function(exports){

  exports.vis = new CrawlerVis();

  // Build the seed crawler and instantiate the necessary plot objects.
  exports.vis.initUISeedCrawler.call(exports.vis);

  exports.inds = [];
  exports.session = {};


  // Updates the session information to be sent to the server with
  // exports.getPlotData()
  exports.updateSession = function(){
    exports.session = exports.vis.sessionInfo();
  }


  // Takes urls and tags from Bokeh and changes their tags.
  exports.updateTags = function(selectedUrls, tag, inds){
    exports.inds = inds;
    exports.vis.tagsGallery.applyOrRemoveTag(tag, "Apply", selectedUrls);
  }


  // Shows the selected pages on the pageGallery below the plot.
  exports.showPages = function(inds){
    exports.inds = inds;
    exports.vis.onBrushedPagesChanged(inds);
  }


  // Inserts the bokeh plot at the specified dom element.
  exports.insertPlot = function(plotData){
    $("#pages_landscape").html(plotData);
  }


  // Gets the necessary javascript and HTML for rendering the bokeh plot into
  // the dom.
  exports.getPlotData = function(){
    $.ajax({
      url: "/getBokehPlot",
      type: "POST",
      data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        exports.insertPlot(data.plot);
        exports.vis.onLoadedPages(data.data);
      },
    });
  }


  exports.getEmptyPlot = function(){
    $.ajax({
      url: "/getEmptyBokehPlot",
      type: "GET",
      //data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        exports.insertPlot(data);
      },
    });
  }


  exports.updateData = function(){
    $.ajax({
      url: "/getBokehPlot",
      type: "GET",
      data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        exports.vis.onLoadedPages(data.data);
        exports.vis.onBrushedPagesChanged(exports.inds);
        exports.insertPlot(data.plot);
      },
    });
  }


  // Connect to updateSession to bokeh_get_session signal
  SigSlots.connect(__sig__.bokeh_get_session, exports, exports.updateSession);
  SigSlots.connect(__sig__.bokeh_insert_plot, exports, exports.getPlotData);

  exports.getEmptyPlot();

})(this.BokehPlots = {});
