/**
 * This module handles communication between the bokeh callbacks and the rest of
 * the DDT application. Many of these functions are helper functions called from
 * the bokeh CustomJS callbacks in `vis/bokeh_graphs/clustering.py`.
 */
(function(exports){

  exports.inds = [];
  exports.plot = {};

  // Updates the session information to be sent to the server with
    exports.updateSession = function(){
    exports.session = exports.vis.sessionInfo();
  }

  // Takes urls and tags from Bokeh and changes their tags.
  exports.updateTags = function(selectedUrls, tag, action){
    // Add the tag to tagsgallery if it does not exist. For example a custom tag
    exports.vis.tagsGallery.addItem(tag, false);
    exports.vis.tagsGallery.applyOrRemoveTag(tag, action, selectedUrls, false);
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
    url_index = -1;
    urls = [].concat.apply([], d.urls);
    for(var i in urls){
	if(urls[i] == url){
	    url_index = i;
	    break;
	}
    }
    d.color[url_index] = color;
    renderer.get("data_source").set("data", d);
    renderer.get("data_source").trigger("change");
  };


  // Gets the necessary javascript and HTML for rendering the bokeh plot into
  // the dom.
  exports.getPlotData = function(data){
    Bokeh.index = {};
    exports.insertPlot(data.plot);
    exports.plot = exports.BokehPlotKey()
  }


  exports.getEmptyPlot = function(){
    $.ajax({
      url: "/getEmptyBokehPlot",
      type: "GET",
      success: function(data){
        exports.insertPlot(data);
      },
    });
  }


  exports.updateData = function(updated_tags){
    // Update the data with the new tags  
    var data = exports.vis.pagesLandscape.getPagesData();
    for(var i in data){
	var url = data[i]["url"];
	if(updated_tags[url] != undefined){
	    tags = updated_tags[url];
	    data[i]["tags"] = tags;
	    if(tags.length != 0 && tags[tags.length - 1] != "")
		exports.updatePlotColors(url, tags[tags.length - 1]);
	    else exports.updatePlotColors(url, "Neutral");
	}
    }
    exports.vis.pagesLandscape.setPagesData(data);
    exports.vis.pagesGallery.update();
  }

  exports.clear = function(updated_tags){
    exports.getEmptyPlot();
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
