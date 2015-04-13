/**
 * @fileoverview js Gallery of websites to be labeled.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages a gallery with websites to be labeled.
 * The items can be a simple URL, a thumbnail for each website or a visual representation for a
 * group of websites, such as a word cloud.
 * Interaction is possible through click on options YES, NO and INSPECT, that triggers an external
 * action. Current labels for YES/NO can be accessed through getItems().
 *
 * @param parentContainerId ID for gallery parent div element.
 */
var PagesGallery = function(parentContainerId) {
  var gallery = this;
  this.parentContainerId = parentContainerId;

  // Items in gallery.
  this.items = [];

  // Registers buttons for all positive/all negative.
  d3.selectAll('#pages_items_all_positive')
    .on('click', function() {
      gallery.setAllPositive();
    });
  d3.selectAll('#pages_items_all_negative')
    .on('click', function() {
      gallery.setAllNegative();
    });
  d3.selectAll('#pages_items_all_neutral')
    .on('click', function() {
      gallery.setAllNeutral();
    });
  this.update();
};


/**
 * Returns list of items in the gallery.
 */
PagesGallery.prototype.getItems = function() {
  return this.items;  
};


/**
 * Clears gallery.
 */
PagesGallery.prototype.clear = function() {
  this.items = [];
  this.update();
};


/**
 * Adds items to gallery.
 */
PagesGallery.prototype.addItems = function(items) {
  this.items = this.items.concat(items);
  this.update();
};


/**
 * Updates gallery.
 */
PagesGallery.prototype.update = function() {
  var gallery = this;
  var items = d3.select(this.parentContainerId)
    .selectAll('.item').data(this.items, function(item, i) {
      return item.url + '-' + i;
  });

  // New items.
  var newItems = items
    .enter()
      .append('div')
      .classed('noselect', true)
      .classed('item', true)
      .on('dblclick', function(item, i) {
        var elem = d3.select(this);
        elem.classed('dblclicked', !elem.classed('dblclicked'));
        gallery.onItemDoubleClick(item, i);
      })
      .on('click', function(item, i) {
        var isShiftKeyPressed = d3.event.shiftKey;
        if (!isShiftKeyPressed) {
          var elem = d3.select(this);

          if (elem.classed('positive')) {
            elem.classed('positive', false);
            elem.classed('negative', true);
            item.label = 'negative';
          } else if (elem.classed('negative')) {
            elem.classed('negative', false);
            item.label = undefined;
          } else {
            elem.classed('positive', true);
            item.label = 'positive';
          }
        }

        gallery.onItemClick(item, i, d3.event.shiftKey, d3.mouse(this));
      })
      .on('mouseover', function(item, i) {
        Utils.showTooltip();
      })
      .on('mousemove', function(item, i) {
        Utils.updateTooltip(item.url);
      })
      .on('mouseout', function(item, i) {
        Utils.hideTooltip();
      });
  //newItems
  //  .append('img');
  newItems
    .append('div')
    .attr('id', function(item, i) {
      return 'item_info-' + i;
    })
    .attr('url', function(item, i) {
      return item.url;
    })
    .classed('item_info', true)
    .classed('noselect', true);
  // Remove missing items.
  items.exit().remove();

  // Updates existing items.
  items
    .classed('positive', function(item, i) {
      return item.label === 'positive';
    })
    .classed('negative', function(item, i) {
      return item.label === 'negative';
    });

  //items.selectAll('img')
  //  .attr('src', function(item, i) {
  //    return item.thumbnail;
  //  });
  items.selectAll('div.item_info')
    .html(function(item, i) {
      return gallery.getItemInfo(item, i);
    });
  items.each(function(item, i) {
    var elemId = '#item_info-' + i;
    var elem = $(elemId);
    elem.urlive({
        container: elemId,
    });
  });

  // Updates visibility of buttons according to number of items in the gallery.
  d3.selectAll('.pages_items_button')
    .style('visibility', (gallery.items.length == 0) ? 'hidden' : null);
};


/**
 * Builds html content with info about an item in the gallery,
 * such as url, number of pages in the cluster etc.
 */
PagesGallery.prototype.getItemInfo = function(item, i) {
  // TODO Add more details about page.
  return '<p>' + item.url + '</p>';
};


/**
 * Handles click in an item.
 */
PagesGallery.prototype.onItemClick = function(item, i, isShiftKeyPressed, mousePosition) {
  // TODO.
  console.log('itemClicked ' + i);
  if (isShiftKeyPressed) {
    var url = item.url;
    if (url.indexOf('http') !== 0) {
      url = 'http://' + url;
    }
    this.setPagePreviewEnabled(true, url, mousePosition);
  } else {
    __sig__.emit(__sig__.pages_labels_changed);
  }
};


/**
 * Handles double click in an item.
 */
PagesGallery.prototype.onItemDoubleClick = function(item, i) {
  // TODO.
  console.log('itemDoubleClicked ' + i);
};


/**
 * Handles click in 'set all positive' button.
 */
PagesGallery.prototype.setAllPositive = function() {
  if (this.items.length == 0) {
    return;
  }
  for (var i in this.items) {
    this.items[i].label = 'positive';
  }
  this.update();
  __sig__.emit(__sig__.pages_labels_changed);
};


/**
 * Handles click in 'set all negative' button.
 */
PagesGallery.prototype.setAllNegative = function() {
  if (this.items.length == 0) {
    return;
  }
  for (var i in this.items) {
    this.items[i].label = 'negative';
  }
  this.update();
  __sig__.emit(__sig__.pages_labels_changed);
};


/**
 * Handles click in 'set all neutral' button.
 */
PagesGallery.prototype.setAllNeutral = function() {
  if (this.items.length == 0) {
    return;
  }
  for (var i in this.items) {
    this.items[i].label = undefined;
  }
  this.update();
  __sig__.emit(__sig__.pages_labels_changed);
};


/**
 * Sets visibility of url preview.
 */
PagesGallery.prototype.setPagePreviewEnabled = function(enabled, url, mousePosition) {
  var gallery = this;
  if (enabled) {
    var transitionTimeInMili = 2000;
    d3.select('#urlBgMask')
      .style('display', 'block')
      .style('opacity', 0)
      .transition(transitionTimeInMili)
      .style('opacity', 0.9);
    d3.select('#mask')
      .style('display', 'block')
      .style('cursor', 'pointer')
      .on('click', function() {
        var isShiftKeyPressed = d3.event.shiftKey;
        if (isShiftKeyPressed) {
          Utils.openInNewTab(url);
        } else {
          gallery.setPagePreviewEnabled(false);
        }
      });

    // TODO: should keep track of width defined in css.
    var iframeWidth = 800;
    var top = d3.event.y;
    var left = d3.event.x - iframeWidth / 2;
    left = Math.max(0, Math.min(left, window.innerWidth - iframeWidth - 20));

    d3.selectAll('iframe#urlPreview').data(['urlPreview'])
        .enter()
      .append('iframe')
      .attr('id', 'urlPreview')
      .attr('src', url)
      .style('opacity', 0)
      .style('top', top + 'px')
      .style('left', left + 'px')
      .transition(transitionTimeInMili)
      .style('opacity', 1);
    d3.select('body')
      .on('keydown', function() {
        if (!d3.event.shiftKey) {
          gallery.setPagePreviewEnabled(false);
        }
      });
  } else {
    d3.select('#urlBgMask')
      .style('display', 'none');
    d3.select('#mask')
      .style('display', 'none')
      .style('cursor', 'wait');
    d3.selectAll('#urlPreview')
      .remove();
    d3.select('body')
      .on('keydown', null);
  }
};
