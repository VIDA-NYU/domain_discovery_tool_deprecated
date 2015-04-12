// TODO remove!
var createBubbleChartData = function(data) {
  return data.map(function(d, i) {
      // x, y, frequency.
      return [d[0], d[1], Math.random()];
  });
};

var BubbleChart = function(containerId) {
    this.containerId = containerId;
    this.MIN_RADIUS = 5;
    this.MAX_RADIUS = 30;
};

BubbleChart.prototype.draw = function(topics, terms, pcaData) {
    var chart = this;
    
    this.topics = topics;
    this.labels = terms;

    // pca data: variance in 1st and 2nd dimensions, and transformed topics.
    var pcaTransformedData = pcaData[1];
    var data = createBubbleChartData(pcaTransformedData);

    // Dimensions.
    var margin = {
          top: chart.MAX_RADIUS + 2, right: chart.MAX_RADIUS + 2,
          bottom: chart.MAX_RADIUS + 2, left: chart.MAX_RADIUS + 2},
        containerWidth = $('#' + this.containerId).width(),
        containerHeight = $('#' + this.containerId).height(),
        width = containerWidth - margin.left - margin.right,
        height = containerHeight - margin.top - margin.bottom;

    // Linear scales for axes and bubbles sizes.
    var xExtent = d3.extent(data, function(p, i) { return p[0]; });
    if (xExtent[0] == xExtent[1]) {
      xExtent[0] -= 1;
      xExtent[1] += 1;
    }

    var yExtent = d3.extent(data, function(p, i) { return p[1]; });
    if (yExtent[0] == yExtent[1]) {
      yExtent[0] -= 1;
      yExtent[1] += 1;
    }

    var xScale = d3.scale.linear().domain(xExtent).range([0, width]);
    var yScale = d3.scale.linear().domain(yExtent).range([height, 0]);
    var sizeScale = d3.scale.linear()
        .domain(d3.extent(data, function(p, i) { return p[2]; }))
        .range([chart.MIN_RADIUS * chart.MIN_RADIUS, chart.MAX_RADIUS * chart.MAX_RADIUS]);
    
    // SVG is for entire panel.
    var svg = d3.select('#' + this.containerId).selectAll('svg').data(['svg']);
    svg.enter().append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight);

    // Grid.
    //var numberOfTicks = 5;

    //var yAxisGrid = d3.svg.axis().scale(yScale)
    //    .ticks(numberOfTicks) 
    //    .tickSize(containerWidth, 0)
    //    .tickFormat('')
    //    .orient('right');

    //var xAxisGrid = d3.svg.axis().scale(xScale)
    //    .ticks(numberOfTicks) 
    //    .tickSize(-containerHeight, 0)
    //    .tickFormat('')
    //    .orient('top');

    //svg.append('g')
    //    .classed('y', true)
    //    .classed('axis', true)
    //    .call(yAxisGrid);

    //svg.append('g')
    //    .classed('x', true)
    //    .classed('axis', true)
    //    .call(xAxisGrid);

    // Group is for inner panel (to guarantee margin and avoid cutting bubbles.
    svg = svg.selectAll('g').data(['svg.g']);
    svg.enter().append('g')
        .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');

    // Creates bubbles.
    var bubbles = svg.selectAll('circle.bubble').data(data);
    bubbles.enter().append('circle')
        .classed('bubble', true);
    bubbles
        .attr('cx', function(point, i) { return xScale(point[0]); })
        .attr('cy', function(point, i) { return yScale(point[1]); })
        .attr('r', function(point, i) {
            var r = Math.sqrt(sizeScale(point[2]));
            return r;
        })
        .on('click', function(d, i) {
            onSelectTopic(chart.topics[i], chart.labels);
        })
    bubbles.exit().remove();
};
