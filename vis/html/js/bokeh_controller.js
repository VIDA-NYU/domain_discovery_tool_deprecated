(function(exports){

  var vis = new CrawlerVis();
  exports.session = {};
  exports.plotData = {};


  exports.updateData = function(){
    exports.session = vis.sessionInfo();
  }


  SigSlots.connect(__sig__.bokeh_get_session, exports, exports.updateData);

})(this.BokehPlots = {});
