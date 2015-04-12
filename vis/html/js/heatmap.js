/**
 * Simple heat map.
 *
 * March 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */


var HeatMap = function(containerId, opt_colorsNegative) {
  this.containerId = containerId;

  this.PADDING = 10;
  this.TOTAL_MARGIN = 2.5 * this.PADDING;
  this.colors = opt_colorsNegative ? 
    ['#ffffff', '#fef0d9', '#fdd49e', '#fdbb84', '#fc8d59', '#e34a33', '#b30000'] : // yellow-red
    ['#ffffff', '#eff3ff', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];  // blueish
    //['#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#99000d']; // redish.
  // || ['#ffffff', '#edf8e9', '#c7e9c0', '#a1d99b', '#74c476', '#31a354', '#006d2c'];  // red
};


// Redraws with new data.
HeatMap.prototype.draw = function(data, title) {
  var chart = this;

  this.data = data;

  var colors = this.colors;
  var color = d3.scale.linear()
    .range(colors)
    .domain(colors.map(function(d, i) { return i / colors.length; }));

  // Gets container dimensions to compute width/height.
  var width = $('#' + this.containerId).width();
  var height = $('#' + this.containerId).height();
  var panelWidth = Math.min(width, height);

  var cellDim = (panelWidth - this.TOTAL_MARGIN) / data.length;
  var marginTop = 15;

  var svg = d3.select('#' + this.containerId).selectAll('svg').data(['svg']);
  svg.enter().append('svg')
    .attr('width', panelWidth)
    .attr('height', panelWidth);

  var textTitle = svg.selectAll('text.title').data(['title']);
  textTitle.enter()
      .append('text')
      .classed('title', true)
      .classed('noselect', true);
  textTitle
      .attr('x', panelWidth / 2)
      .attr('y', 15)
      .text(title);

  svg = svg.selectAll('g').data(['svg.g']);
  svg.enter().append('g')
      .attr('transform', 'translate(' + this.PADDING + ', ' + (marginTop + this.PADDING) + ')');

  var rows = svg.selectAll('.row').data(data);

  rows.enter().append('g')
      .classed('row', true);
  rows.attr('transform', function(d, i) {
      var xTranslation = 0;
      var yTranslation = i * cellDim;
          return 'translate(' + xTranslation + ', ' + yTranslation + ')';
      });
  rows.exit().remove();

  var cells = rows.selectAll('.cell').data(function(rowInData) { return rowInData; });
  cells.enter().append('rect').classed('cell', true);
  cells
      .attr('x', function(d, i) {
          return i * cellDim;
      })
      .attr('y', 0)
      .attr('width', cellDim)
      .attr('height', cellDim)
      .style('fill', function(d, i) {
          return color(d);
      });
  cells.exit().remove();
};
