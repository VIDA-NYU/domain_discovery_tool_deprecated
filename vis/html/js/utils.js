/**
 * @fileoverview Contains commonly used functions throughout the
 * application.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */
var Utils = (function() {
  var tooltipDiv = undefined;
  var pressedKey = undefined;

  // Creates a div for tooltip content.
  var maybeCreateTooltip = function() {
    if (tooltipDiv === undefined) {
      tooltipDiv = d3.select('body')
        .append('div')
          .classed('tooltip', true)
          .style('opacity', 1e-6);
    }
  };

  // Registers window to listen for pressed keys.
  d3.select(window).on('keydown', function() {
    pressedKey = d3.event.keyCode;
  });
  d3.select(window).on('keyup', function() {
    pressedKey = undefined;
  });

  var pub = {};
  pub.showTooltip = function() {
    maybeCreateTooltip();
    tooltipDiv.transition()
      .duration(500)
      .style('opacity', 1);
  };
  pub.hideTooltip = function() {
    maybeCreateTooltip();
    tooltipDiv.transition()
      .duration(500)
      .style('opacity', 1e-6);
  };
  pub.updateTooltip = function(text, opt_x, opt_y) {
    maybeCreateTooltip();
    var x = opt_x || d3.event.pageX + 5;
    var y = opt_y || d3.event.pageY - 12;
    tooltipDiv
      .text(text)
      .style('left', x + 'px')
      .style('top',  y + 'px');
  };
  pub.setWaitCursorEnabled = function(enabled) {
    d3.select('#mask')
      .style('display', enabled ? 'block' : 'none')
      .style('cursor', enabled ? 'wait' : 'pointer');
  };
  pub.getRandomInt = function(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
  };
  pub.openInNewTab = function(url) {
    var win = window.open(url, '_blank');
    win.focus();
  };
  pub.isKeyPressed = function(key) {
    return pressedKey === key;
  };
  return pub;
}());
