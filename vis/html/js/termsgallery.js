/**
 * @fileoverview js Gallery of frequent terms.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages a gallery with frequent terms appearing in URLs.
 * Interaction is possible through click on options YES, NO and INSPECT, that triggers an external
 * action.
 *
 * @param parentContainerId ID for gallery parent div element.
 */
var TermsGallery = function(parentContainerId) {
  this.parentContainerId = parentContainerId;

  // Items in gallery.
  this.items = [];

  this.update();
};


/**
 * Returns list of items in the gallery.
 */
TermsGallery.prototype.getItems = function() {
  return this.items;
};


/**
 * Clears list of items.
 */
TermsGallery.prototype.clear = function(lazyUpdate) {
  this.items = [];
  if (!lazyUpdate) {
    this.update();
  }
};


/**
 * Adds item to gallery.
 */
TermsGallery.prototype.addItem = function(term, lazyUpdate) {
  this.items.push(term);
  if (!lazyUpdate) {
    this.update();
  }
};


/**
 * Updates gallery.
 */
TermsGallery.prototype.update = function() {
  var gallery = this;
  var items = d3.select(this.parentContainerId)
    .selectAll('.item').data(this.items, function(item, i) {
      return item + '-' + i;
  });

  // New items.
  items.enter()
    .append('div')
    .classed('noselect', true)
    .classed('item', true);

  // Remove missing items.
  items.exit().remove();

  // Updates existing items.
  items
    .on('dblclick', function(item, i) {
      if (d3.event.shiftKey) {
        var elem = d3.select(this);
        elem.classed('dblclicked', !elem.classed('dblclicked'));
        gallery.onItemDoubleClick(item, i);
      }
    })
    .on('click', function(item, i) {
      var elem = d3.select(this);

      // Shift click equals double click behavior.
      if (d3.event.shiftKey) {
        return;
      } else {
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

        gallery.onItemClick(item, i);
        gallery.onItemSelected(item, i);
      }
    })
    .on('mouseover', function(item, i) {
      gallery.onItemSelected(item, i);
    })
    .classed('positive', function(item, i) {
      return item.label === 'positive';
    })
    .classed('negative', function(item, i) {
      return item.label === 'negative';
    })
    .html(function(item, i) {
      return gallery.getItemInfo(item, i);
    });

  // Updates visibility of buttons according to number of items in the gallery.
  d3.selectAll('.terms_interface')
    .style('visibility', (gallery.items.length == 0) ? 'hidden' : null);
};


/**
 * Builds html content with info about an item in the gallery.
 */
TermsGallery.prototype.getItemInfo = function(item, i) {
  // TODO Add more details about term.
  return '<p>' + item.term + '</p>';
};


/**
 * Builds html content with buttons for labeling relevancy an item in the gallery,
 * such as Yes, No, Maybe.
 */
TermsGallery.prototype.getItemLabels = function(item, i) {
  // TODO.
  return '<p>Yes No Maybe</p>';
};


/**
 * Handles click in an item.
 */
TermsGallery.prototype.onItemClick = function(item, i) {
  // TODO.
};


/**
 * Handles click in an item.
 */
TermsGallery.prototype.onItemDoubleClick = function(item, i) {
  __sig__.emit(__sig__.add_term_to_query_box, item.term);
};


/**
 * Handles item selection.
 */
TermsGallery.prototype.onItemSelected = function(item, i) {
  __sig__.emit(__sig__.term_selected, item);
};
