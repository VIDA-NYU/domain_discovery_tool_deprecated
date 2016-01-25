(function(exports){

  exports.visSettings = {
    tokenizer: "simple",
    vectorizer: "bag_of_words",
    model: "plsa",
    ntopics: 2,
    visualizer: "",
    domain: "",
  }


  $("#ldavisPlot, #termitePlot").on("click", function(){
    exports.visSettings.visualizer = $(this).attr("value");
    exports.visSettings.domain = $('input[name="crawlerRadio"]:checked').attr("placeholder").toLowerCase()
    var url = "/topicsvis?" + $.param(exports.visSettings);
    $(this).attr("href", url);
  });

})(this.TopikVis = {});
