/**
 * @fileoverview js Statistics for crawled pages (for seed crawler).
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages a list of statistics of crawled pages, including Relevant/Irrelevant/Neutral
 * pages (for seed crawler).
 *
 * @param containerId ID for parent element.
 */
var Statslist = function(containerId) {
    this.containerId = containerId;  
    this.entries = [];
    this.setMaxBarTotal(100);
    this.update();
};


Statslist.prototype.setMaxBarTotal = function(maxBarTotal) {
    this.maxBarTotal = maxBarTotal;
    this.update();
};


Statslist.prototype.addEntries = function(entries) {
    this.entries = this.entries.concat(entries);
    this.update();
};


Statslist.prototype.setEntries = function(entries) {
    this.entries = entries;
    this.update();
};


Statslist.prototype.setMaxStatValue = function(maxStatValue) {
    this.maxStatValue = maxStatValue;
    this.update();
};

Statslist.prototype.update = function() {
    var statslist = this;
    var maxWordTextWidth = 120;
    var rowHeight = 30;
    var barHeight = 20;
    var svgMargin = {'top': 5, 'left': 5, 'right': 5};
    
    var containerWidth = $('#' + statslist.containerId).width();
    var width = containerWidth - svgMargin.left - svgMargin.right;
    var maxBarWidth = width - maxWordTextWidth;

    var numberFormat = d3.format('0,000');
    var transitionDuration = 500;
    
    var svg = d3.select('#' + this.containerId).select('svg');
    svg = svg.selectAll('g.rowsContainer').data(['g.rowsContainer']);
    svg.enter().append('g')
        .classed('rowsContainer', true)
        .attr('transform', 'translate(' + svgMargin.left + ', ' + svgMargin.top + ')');
    
    // Number of pages per entry.
    // TODO(cesar): Make this flexible.
    var nPages = this.entries.map(function(d) {
        return d['Relevant'] + d['Irrelevant'] + d['Neutral'];
    });
    statslist.nPagesPerEntry = {};
    for (var i in nPages) {
      statslist.nPagesPerEntry[statslist.entries[i]['name']] = nPages[i];   
    }
    statslist.nPagesTotal = nPages.reduce(function(prev, cur) { return prev + cur; }, 0);
    
    var titleRow = svg.selectAll('g.titleRow').data(['titleRow']);
    titleRow
        .enter().append('g')
        .classed('titleRow', true);
    var titleText = titleRow.selectAll('text').data(['text']);
    titleText
        .enter().append('text')
        .classed('caption', true)
        .attr('y', 0.5 * rowHeight);
    titleText.text('Crawled pages: ' + numberFormat(statslist.nPagesTotal));    
    
    
    // Rows for entries.
    var rows = svg.selectAll('g.row').data(statslist.entries, function(d, i) {
        return i + '-' + d['name'];
    });
    rows.exit().remove();
    rows.enter().append('g')
        .classed('row', true)
        .attr('transform', function(d, i) {
            return 'translate(0, '
            + ((i + 1) * rowHeight) + ')'; 
        });

    // Container for stats names.
    var names = rows.selectAll('g.names').data(function(d) { return [d]; });
    names
      .enter().append('g')
        .classed('names', true)
        .attr('transform',
              'translate(0,' + (0.5 * rowHeight) + ')')
        .append('text')
        .classed('caption', true)
        .classed('noselect', true)
        .text(function(d) { return d['name']; });

    // Scales for bars.
    var barScale = d3.scale.linear()
        .range([0, maxBarWidth])
        .domain([0, statslist.maxBarTotal]);

    // Containers for bars.
    var barsContainers = rows.selectAll('g.bar').data(function(d) { return [d]; });
    barsContainers.enter().append('g')
        .classed('bar', true)
        .classed('positive', function(d) { return d['label'] == 'positive'; })
        .classed('negative', function(d) { return d['label'] == 'negative'; })
        .attr('transform', 'translate(' + (svgMargin.left + maxWordTextWidth) + ', 0)');
    
    // TODO(cesar): Make this flexible.
    barsContainers.each(function(d, i) {
        // Rectangle for number of relevant pages.
        var rectExplored = d3.select(this).selectAll('rect.Relevant').data(['rect']);
        rectExplored.enter().append('rect')
            .classed('Relevant', true)
            .attr('y', 0.5 * (rowHeight - barHeight))
            .attr('height', barHeight);
        var widthExplored = barScale(d['Relevant']);
        var xExplored = 0;
        rectExplored
          .transition(transitionDuration)
          .attr('x', xExplored)
          .attr('width', widthExplored);
        
        // Rectangle for number of irrelevant pages.
        var rectExploited = d3.select(this).selectAll('rect.Irrelevant').data(['rect']);
        rectExploited.enter().append('rect')
            .classed('Irrelevant', true)
            .attr('y', 0.5 * (rowHeight - barHeight))
            .attr('height', barHeight);
        var widthExploited = barScale(d['Irrelevant']);
        var xExploited = widthExplored;
        rectExploited
          .transition(transitionDuration)
          .attr('x', xExploited)
          .attr('width', widthExploited);
        
        // Rectangle for number of neutral pages.
        var rectNew = d3.select(this).selectAll('rect.Neutral').data(['rect']);
        rectNew.enter().append('rect')
            .classed('Neutral', true)
            .attr('y', 0.5 * (rowHeight - barHeight))
            .attr('height', barHeight);
        var widthNew = barScale(d['Neutral']);
        var xNew = widthExplored + widthExploited;
        rectNew
          .transition(transitionDuration)
          .attr('x', xNew)
          .attr('width', widthNew);
    });

    // Interaction rectangle.
    rows.selectAll('rect.interaction').data(function(d, i) { return [d]; })
      .enter().append('rect').classed('interaction', true)
        .attr('x', -svgMargin.left)
        .attr('width', containerWidth)
        .attr('height', rowHeight)
        .on('click', function(d, i) {
            console.log('click on stat ', d['name']);
        })
        .on('mouseover', function(d, i) {
            Utils.showTooltip();
        })
        .on('mousemove', function(d, i) {
            var t = numberFormat(statslist.nPagesPerEntry[d['name']]) + ' ' + d['label']
              + ' pages out of ' + numberFormat(statslist.nPagesTotal) + ' crawled';
            Utils.updateTooltip(t);
        })
        .on('mouseout', function(d, i) {
            Utils.hideTooltip();
        });
};
