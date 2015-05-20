var Wordlist = function(containerId) {
    this.containerId = containerId;  
    this.entries = [];
    this.setMaxPosNegFreq(100, 100);
    this.update();
};10


Wordlist.prototype.setMaxPosNegFreq = function(maxPosFreq, maxNegFreq) {
    this.maxPosFreq = maxPosFreq;
    this.maxNegFreq = maxNegFreq;
    this.update();
};


Wordlist.prototype.addEntries = function(entries) {
    this.entries = this.entries.concat(entries);
    this.update();
};


Wordlist.prototype.setEntries = function(entries) {
    this.entries = entries;
    this.update();
};


Wordlist.prototype.update = function() {
    var wordlist = this;
    var maxWordTextWidth = 100;
    var rowHeight = 16;
    var barHeight = 6;
    var svgMargin = {'top': 5, 'left': 5, 'right': 5, 'bottom': 5};
    
    var containerWidth = $('#' + wordlist.containerId).width();
    var width = containerWidth - svgMargin.left - svgMargin.right;
    var maxBarWidth = 0.5 * (width - maxWordTextWidth);

    // Computes svg height.
    var svgHeight = svgMargin.top + svgMargin.bottom + rowHeight * this.entries.length;


    var transitionDuration = 500;
    
    var svg = d3.select('#' + this.containerId).selectAll('svg').data(['svg']);
    svg.enter().append('svg');
    svg.attr('height', svgHeight);
    svg = svg.selectAll('g.container').data(['g.container']);
    svg.enter().append('g')
        .classed('container', true)
        .attr('transform', 'translate(' + svgMargin.left + ', ' + svgMargin.top + ')');
    
    // Rows for entries.
    var rows = svg.selectAll('g.row').data(wordlist.entries, function(d, i) {
        return i + '-' + d['word'];
    });
    rows.exit().remove();
    rows.enter().append('g')
        .classed('row', true)
        .attr('transform', function(d, i) {
            return 'translate(0, '
            + (i * rowHeight) + ')'; 
        });

    // Left bars (positive frequency bars).
    var posBars = rows.selectAll('g.bar.pos').data(function(d) { return [d]; });
    posBars.enter().append('g')
        .classed('bar', true)
        .classed('pos', true)
      .append('rect')
        .classed('background', true)
        .attr('y', 0.5 * (rowHeight - barHeight))
        .attr('width', maxBarWidth)
        .attr('height', barHeight);

    // Container for word.
    var words = rows.selectAll('g.words').data(function(d) { return [d]; });
    words
      .enter().append('g')
        .classed('words', true)
        .attr('transform',
              'translate(' + (maxBarWidth + 0.5 * maxWordTextWidth) + ',' + (0.5 * rowHeight) + ')')
        .append('text')
        .classed('noselect', true)
        .text(function(d) { return d['word']; });

    // Interaction rectangle.
    rows.selectAll('rect.interaction').data(function(d, i) { return [d]; })
      .enter().append('rect').classed('interaction', true)
        .attr('width', width)
        .attr('height', rowHeight)
        .on('click', function(d) {
            console.log('click on word ', d['word']);
        })
        .on('mouseover', function(d) {
            __sig__.emit(__sig__.term_focus, d['word'], true);
        })
        .on('mouseout', function(d) {
            __sig__.emit(__sig__.term_focus, d['word'], false);
        });

    // Right bars (negative frequency bars).
    var negBars = rows.selectAll('g.bar.neg').data(function(d) { return [d]; });
    negBars.enter().append('g')
        .classed('bar', true)
        .classed('neg', true)
        .attr('transform', 'translate(' + (maxBarWidth + maxWordTextWidth) + ', 0)')
      .append('rect')
        .classed('background', true)
        .attr('y', 0.5 * (rowHeight - barHeight))
        .attr('width', maxBarWidth)
        .attr('height', barHeight);
    
    // Scales for left/right bars.
    // TODO Read domain from data.
    var barScale = d3.scale.linear()
        .range([0, maxBarWidth]);
    
    // Adds left bars (aligned to right).
    barScale.domain([0, wordlist.maxPosFreq]);
    posBars.each(function(d, i) {
        var rect = d3.select(this).selectAll('rect.pos').data(['rect']);
        rect.enter().append('rect')
            .classed('pos', true)
            .attr('y', 0.5 * (rowHeight - barHeight))
            .attr('height', barHeight);
        // Aligns left bar to right.
        var width = barScale(d['posFreq']);
        rect
          .transition(transitionDuration)
          .attr('x', maxBarWidth - width)
          .attr('width', width);
    });
   
    // Adds right bars (aligned to left).
    barScale.domain([0, wordlist.maxNegFreq]);
    negBars.each(function(d, i) {
        var rect = d3.select(this).selectAll('rect.neg').data(['rect']);
        rect.enter().append('rect')
            .classed('neg', true)
            .attr('y', 0.5 * (rowHeight - barHeight))
            .attr('height', barHeight);

        // Aligns left bar to left.
        var width = barScale(d['negFreq']);
        rect
          .transition(transitionDuration)
          .attr('x', 0)
          .attr('width', width);
    });
};
