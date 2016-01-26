(function(exports){

  /**
   * Sting to be used when grabbing the settings form DOM element.
   */
  var form = "#topicvis_settings_form";


  /**
   * Default settings for the topik visualizations.
   */
  exports.visSettings = {
    tokenizer: "simple",
    vectorizer: "bag_of_words",
    model: "plsa",
    ntopics: 2,
    visualizer: "",
    domain: "",
  };


  /**
   * Convert the values in the form to simple key-value pairs, in which the key
   * is the html name of the input and the value is the value of the input.
   */
  exports.formToObject = function(form){
    var objects = {};
    var formData = $(form).serializeArray();
    for(var i = 0; i < formData.length; i++){
      objects[formData[i]["name"]] = formData[i]["value"]
    }
    return objects;
  }


  /**
   * Update visSettings with the new settings using jQuery.extend
   */
  exports.updateSettings = function(){
    $.extend(true, exports.visSettings, exports.formToObject(form));
  }


  /**
   * When either button is clicked, use the context dependent "this" to
   * grab the value of the clicked button and update visSettings, then change
   * the href on the link button to contain the vis settings parsed as URL
   * paramaters.
   */
  $("#ldavisPlot, #termitePlot").on("click", function(){
    exports.visSettings.visualizer = $(this).attr("value");
    exports.visSettings.domain = $('input[name="crawlerRadio"]:checked')
      .attr("placeholder").toLowerCase()
    var url = "/topicvis?" + $.param(exports.visSettings);
    $(this).attr("href", url);
  });


  /**
   * When the save button is clicked, update visSettings with the new values
   * from the form.
   */
  $("#save_topicvis_settings").on("click", function(){
    exports.updateSettings();
    $("#topicVisSettingsModal").modal("hide");
  });


  /**
   * Update the ntopic select field with 23 integer values. The default will be
   * the first in the list of options. This is done to iteratively create 23
   * options without having to manually add them to the DOM element.
   */
  $(document).ready(function(){
    for(var i = 2; i < 24; i++){
      var option = "<option value='" + i + "'>" + i + "</option>"
      $("#ntopics").append(option);
    }
  });

})(this.TopicVis = {});
