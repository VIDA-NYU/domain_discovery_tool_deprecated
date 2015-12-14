(function(exports){

  var vis = new CrawlerVis();

  exports.session = {};
  exports.plotData = {};


  exports.updateSession = function(){
    exports.session = vis.sessionInfo();
    exports.getPlotData();
  }

  exports.insertPlot = function(){
    $("#bokehClusterPlot").html(exports.plotData);
  }


  exports.getPlotData = function(){
    $.ajax({
      url: "/getBokehPlot",
      type: "POST",
      data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        exports.plotData = data;
      },
    });
  }


  // Connect to updateSession to bokeh_get_session signal
  SigSlots.connect(__sig__.bokeh_get_session, exports, exports.updateSession);
  SigSlots.connect(__sig__.bokeh_insert_plot, exports, exports.insertPlot);

})(this.BokehPlots = {});
