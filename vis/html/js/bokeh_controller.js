(function(exports){

  var vis = new CrawlerVis();

  exports.session = {};
  exports.plotData = {};


  exports.updateSession = function(){
    exports.session = vis.sessionInfo();
  }

  exports.insertPlot = function(){
    $("#clusterPlot").html(exports.plotData);
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

})(this.BokehPlots = {});
