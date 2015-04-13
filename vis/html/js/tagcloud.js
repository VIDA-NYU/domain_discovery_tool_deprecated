/**
 * Tag cloud.
 * TODO Allow brushing.
 *
 * March 2015.
 * @author Cesar Palomo <cesarpalomo@gmail.com> <cmp576@nyu.edu>
 */

// TODO remove!
var getIndicesAndCountOfRelevantWords = function(topicDistribution, opt_numberOfWords) {
  // TODO use saliency or tf-idf to choose relevant words.
  var numberOfWords = opt_numberOfWords || 20;
  var sortedDescending = topicDistribution.map(function(d, i) {
    return {'size': d, 'index': i};
  }).sort(function(entry1, entry2) {
      // Descending order (top words).
      return entry1['size'] > entry2['size'] ? -1 : 1;
  });
  return sortedDescending.slice(0, numberOfWords);
};


// TODO remove!
var createTagCloudData = function(topicDistribution, terms) {
  var topWords = getIndicesAndCountOfRelevantWords(topicDistribution);
  return topWords.map(function(entry) {
      var size = entry['size'],
          wordIndex = entry['index'];
      return {'text': terms[wordIndex], 'size': size};
  });
};


var TagCloud = function(containerId, opt_data) {
  this.containerId = containerId;
  if (opt_data) {
    this.draw(opt_data);
  }
};


/** Redraws with new data in the format:
 * [{'text':'study','size':40},{'text':'motion','size':15},...];
 */
TagCloud.prototype.draw = function(data, title) {
    var chart = this;

    var fontScale = d3.scale.linear()
        .domain(d3.extent(data, function(d) { return d['size']; }))
        .range([10, 20]);

    // Color scale inversely proportional to frequency.
    var colorScale = d3.scale.linear()
        .domain(d3.extent(data, function(d, i) {
            return fontScale(d['size']);
        }))
        .range(['#222', '#cfcfcf']);

    // Dimensions.
    // TODO read dimensions from container.
    var padding = 10,
        width = 160,
        height = 60;
        // width = $('#' + this.containerId).width(),
        // height = $('#' + this.containerId).height();

    var svg = d3.select('#' + this.containerId).selectAll('svg').data(['svg']);
    svg.enter().append('svg')
      .attr('width', width + 2 * padding)
      .attr('height', height + 2 * padding);

    svg = svg.selectAll('g').data(['svg.g']);
    svg.enter().append('g')
        .attr('transform', 'translate(' + (padding + 0.5 * width) + ', ' + (padding + 0.5 * height) + ')');

    var layout = d3.layout.cloud()
        .size([width, height])
        .timeInterval(10)
        .text(function(d) { return d.text; })
        .font('Impact')
        .fontSize(function(d) { return fontScale(+d.size); })
        .rotate(function(d) {
            //return ~~(Math.random() * 5) * 15 - 30;
            return 0;
        })
        .padding(1)
        //.on('word', progress)
        .on('end', drawWords)
        .words(data)
        .start();

    function drawWords(words) {
        var textWords = svg.selectAll('text').data(words);
        textWords.enter().append('text').classed('term', true).classed('noselect', true);
        textWords
            .style('font-size', function(d) {
                return d.size + 'px';
            })
            .style('fill', function(d, i) {
                return colorScale(d.size);
            })
            .attr('transform', function(d) {
                return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')';
            })
            .text(function(d) { return d.text; });
        textWords.exit().remove();
    }
};
