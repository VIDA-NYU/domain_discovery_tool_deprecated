/**
 * This module handles communication between the bokeh callbacks and the rest of
 * the DDT application. Many of these functions are helper functions called from
 * the bokeh CustomJS callbacks in `vis/bokeh_graphs/clustering.py`.
 */
(function(exports){

  exports.inds = [];
  exports.session = {};
  exports.plot = {};


  // Updates the session information to be sent to the server with
  // exports.getPlotData()
  exports.updateSession = function(){
    exports.session = exports.vis.sessionInfo();
  }


  // Takes urls and tags from Bokeh and changes their tags.
  exports.updateTags = function(selectedUrls, tag, inds){
    exports.updatePagesGallery(tag);
    exports.inds = inds;
    exports.vis.tagsGallery.applyOrRemoveTag(tag, "Apply", selectedUrls, false);
  }


  exports.concatUrls = function(data){
    var urls = [];
    for(var i = 0; i < data.length; i++){
      urls.push(data[i].url)
    }
    urls = [].concat.apply([], urls);
    return urls;
  }


    exports.updatePagesGallery = function(tag){
    $("#pages_items").children().find("span.not-clickable").each(function(item){
      if(tag != "Neutral"){
        $(this).siblings().attr("class", "clickable");
        $(this).text(tag);
      } else {
        $(this).siblings().attr("class", "not-clickable");
        $(this).text("");
      }
    });
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


  exports.BokehPlotKey = function(){
    return Bokeh.index[Object.keys(Bokeh.index)[0]].model.children()[0]
  }


  exports.getGlyphRenderersByType = function(glyphType) {
    var allRenderers = exports.plot.get("renderers");
    var renderers = [];
    $.each(exports.plot.get("renderers"), function(index, value) {
      if (value.attributes.hasOwnProperty("glyph") && value.attributes.glyph.type === glyphType) {
        renderers.push(value);
      }
    });
    return renderers;
  };


    exports.updatePlotColors = function(url, type) {
    var renderer = exports.getGlyphRenderersByType("Circle")[0];
    var d = renderer.get("data_source").get("data");
    if(type == "Relevant"){
      var color = "blue";
    } else if(type == "Irrelevant"){
      var color = "crimson";
    } else if(type == "Neutral"){
	var color = "#7F7F7F";
    } else {
	var color = "green";
    }
    url_index = [].concat.apply([], d.urls).indexOf(url);
    d.color[url_index] = color;
    d.tags[url_index][0] = type;
    renderer.get("data_source").set("data", d);
    renderer.get("data_source").trigger("change");
  };


  // Gets the necessary javascript and HTML for rendering the bokeh plot into
  // the dom.
  exports.getPlotData = function(){
    $.ajax({
      url: "/getBokehPlot",
      type: "POST",
      data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        Bokeh.index = {};
        exports.insertPlot(data.plot);
        exports.plot = exports.BokehPlotKey()
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
      },
    });
  }


  exports.updateDataPlot = function(){
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


  // Statistics page functions and callbacks.
  $("#goto_statistics").on("click", function(){
    var url = "/statistics?" + $.param({session: JSON.stringify(exports.session)});
    $(this).attr("href", url);
  });

})(this.BokehPlots = {});
