(function(exports){

  var vis = new CrawlerVis();

  exports.session = {};
  exports.plotData = {};


  exports.updateSession = function(){
    exports.session = vis.sessionInfo();
  }


  exports.getPlotData = function(){
    $.ajax({
      url: "/getPages",
      type: "POST",
      data: {"session": JSON.stringify(exports.session)},
      success: function(data){
        exports.plotData = data;
      },
    });
  }


  SigSlots.connect(__sig__.bokeh_get_session, exports, exports.updateSession);

})(this.BokehPlots = {});
