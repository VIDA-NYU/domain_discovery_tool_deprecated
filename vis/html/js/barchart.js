/**
 * Bar chart for frequencies. Allows brushing.
 *
 * March 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */

var BarChart = function(containerId, opt_data) {
  this.containerId = containerId;
  if (opt_data) {
    this.draw(opt_data);
  }
};


// Redraws with new data.
BarChart.prototype.draw = function(data, title) {
  var chart = this;

  // TODO(cesar) complete: stopped here.

  var colors = ['#ffffff', '#eff3ff', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];  // yellow-red
  //var colors = ['#ffffff', '#fef0d9', '#fdd49e', '#fdbb84', '#fc8d59', '#e34a33', '#b30000'];  // blue
  //var colors = ['#ffffff', '#edf8e9', '#c7e9c0', '#a1d99b', '#74c476', '#31a354', '#006d2c'];  // red
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


