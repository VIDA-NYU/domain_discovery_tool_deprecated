/**
 * Termite visualization for topics.
 *
 * February 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */


var Termite = function(containerId, opt_colorNegative) {
  this.containerId = containerId;

  this.MAX_RADIUS = 0.5;
  this.PADDING = 80;
  this.TOTAL_MARGIN = 1.5 * this.PADDING;
  this.color = opt_colorNegative ? 'red' : '#0072E8';
};





// TODO remove!
function createMatrix() {
  var NUM_TOPICS = 5;
  var NUM_WORDS = 20;

  var simMatrix = [];
  for (var rowI = 0; rowI < NUM_TOPICS; ++rowI) {
      var row = [];
      for (var colI = 0; colI < NUM_WORDS; ++colI) {
          row.push(Math.random());
      }
      simMatrix.push(row);
  }
  return simMatrix;
}


// Redraws with new data.
Termite.prototype.draw = function(data, labels, title) {
  var chart = this;

  this.data = data;
  this.labels = labels;

  var topicsCount = data.length,
      wordsCount = data[0].length;
  
  // Gets container dimensions to compute width/height.
  var width = $('#' + this.containerId).width();
  var height = $('#' + this.containerId).height();
  var cellWidth = 15 || (width - this.TOTAL_MARGIN) / topicsCount;
  var cellHeight = 15 || (height - this.TOTAL_MARGIN) / wordsCount;
  var marginTop = 10;


  var svg = d3.select('#' + this.containerId).selectAll('svg').data(['svg']);
  svg.enter().append('svg')
    .attr('width', width)
    .attr('height', height);

  var textTitle = svg.selectAll('text.title').data(['title']);
  textTitle.enter()
      .append('text')
      .classed('title', true)
      .classed('noselect', true);
  textTitle
      .attr('x', width / 2)
      .attr('y', 30)
      .text(title);

  svg = svg.selectAll('g').data(['svg.g']);
  svg.enter().append('g')
    .attr('transform', 'translate(' + this.PADDING + ', ' + (marginTop + this.PADDING) + ')');

  // Creates columns for topics.
  var colForTopics = svg.selectAll('g.col').data(data);
  colForTopics.enter().append('g')
      .classed('col', true);
  colForTopics.attr('transform', function(d, i) { return 'translate(' + (i * cellWidth) + ', 0)'; });
  colForTopics.exit().remove();

  var topicLabels = colForTopics.selectAll('text.colLabel').data(function(d, i) {
    // TODO Return topic label.
    return [i];
  });
  topicLabels.enter().append('text')
      .classed('colLabel', true)
      .classed('noselect', true);
  topicLabels
      .attr('x', 10)
      .on('click', function(d, i) {
          onSelectTopic(chart.data[i], chart.labels);
      })
      .text(function(d, i) {
        // TODO Return topic label.
        return 'Topic ' + (d + 1);
      });
  topicLabels.exit().remove();

  var topicLines = colForTopics.selectAll('line.colLine').data(function(d, i) { return [i]; });
  topicLines.enter().append('line')
      .classed('colLine', true);
  topicLines
      .attr('x1', function(i, i) {
          return i * cellWidth;
      })
      .attr('y1', 0)
      .attr('x2', function(i, i) {
          return i * cellWidth;
      })
      .attr('y2', cellHeight * wordsCount);
  topicLines.exit().remove();


  // Creates rows for vocabulary.
  var rowForWords = svg.selectAll('.row').data(d3.range(wordsCount));
  rowForWords.enter().append('g')
    .classed('row', true)
    .attr('transform', function(d, i) {
      var xTranslation = 0;
      var yTranslation = i * cellHeight;
      return 'translate(' + xTranslation + ', ' + yTranslation + ')';
    });
  rowForWords.exit().remove();

  var wordLabels = rowForWords.selectAll('text.rowLabel').data(function(d, i) { return [i]; } );
  wordLabels.enter().append('text')
      .classed('rowLabel', true)
      .classed('noselect', true)
      .attr('x', -chart.MAX_RADIUS - 10)
      .on('click', function(d, i) {
          console.log('click on row ' + d);
      });
  wordLabels.text(function(d, i) {
    return labels[d];
  });
  wordLabels.exit().remove();

  var rowLines = rowForWords.selectAll('line.rowLine').data(function(d, i) { return [i]; });
  rowLines.enter().append('line')
    .classed('rowLine', true);
  rowLines
    .attr('x1', 0)
    .attr('y1', 0)
    .attr('x2', width - this.TOTAL_MARGIN)
    .attr('y2', 0);


  // Draws circles for distribution per topic.
  var cells = rowForWords.selectAll('.cell').data(function(rowIndex, i) {
    return d3.range(topicsCount).map(function(d, i) { return rowIndex; });
  });
  cells.enter().append('circle').classed('cell', true);
  cells
    .attr('cx', function(d, i) {
        return i * cellHeight;
    })
    .attr('cy', 0)
    .attr('r', function(rowIndex, topicIndex) {
      var d = data[topicIndex][rowIndex];
      return chart.MAX_RADIUS * Math.sqrt(d);
    })
    .style('fill', function(d, i) {
        return i == 3 ? chart.color : 'gray';
    })
    .style('stroke', function(d, i) {
        return i == 3 ? chart.color : 'gray';
    });
  cells.exit().remove();
};
