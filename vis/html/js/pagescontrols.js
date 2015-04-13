/**
 * @fileoverview Manages controls for urls to be labeled in seed crawler vis: number of clusters of
 * items to visualize.
 * @author Cesar Palomo (cesarpalomo@gmail.com)
 */


/**
 * Controls urls to be labeled in seed crawler vis: number of clusters of items to visualize.
 *
 * @param parentContainerId ID for gallery parent div element.
 */
var PagesControls = function(parentContainerId) {
  this.parentContainerId = parentContainerId;

  // Creates slider to defined number of clusters to keep.
  this.setClustersCountRange(1, 10, 10);
};


/**
 * Sets range and current value of slider for clusters count.
 */
PagesControls.prototype.setClustersCountRange = function(minValue, maxValue, currentValue) {
  // Removes previous slider, if any.
  d3.select('#clusters_count_slider').selectAll('*').remove();
  delete this.clustersCountSlider;

  var controls = this;

  this.clustersCountSlider = d3.slider()
    .axis(false)
    .min(minValue)
    .max(maxValue)
    .value(currentValue)
    .on('slide', function(evt, value) {
      controls.onClustersCountChanged.call(controls, Math.round(value));
    });
  d3.select('#clusters_count_slider').call(this.clustersCountSlider);
  this.onClustersCountChanged(currentValue);
};


/**
 * Responds to changes in sliders for clusters count.
 */
PagesControls.prototype.onClustersCountChanged = function(newValue) {
  d3.select('#clusters_count_text').text(newValue);
  __sig__.emit(__sig__.clusters_count_changed, newValue);
};
