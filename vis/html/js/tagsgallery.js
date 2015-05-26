/**
 * @fileoverview js Gallery of tags.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages a list of tags used for pages (some predefined and some defined by user).
 * Interaction is possible through click on "tag selected" and "untag selected".
 *
 * @param parentContainerId ID for gallery parent div element.
 * @param predefinedTags list of predefined tags, with label and tag name.
 */
var TagsGallery = function(parentContainerId, predefinedTags) {
  this.parentContainerId = parentContainerId;

  // Predefined items in gallery.
  this.predefinedItems = predefinedTags;

  // User-defined items in gallery.
  this.userItems = [];

  this.update();
};


/**
 * Clears list of items.
 */
TagsGallery.prototype.clear = function(lazyUpdate) {
  this.userItems = [];

  if (!lazyUpdate) {
    this.update();
  }
};


/**
 * Adds item to gallery.
 */
TagsGallery.prototype.addItem = function(tag, lazyUpdate) {
  this.userItems.push({'label': tag, 'tag': tag, 'clickable': true});
  if (!lazyUpdate) {
    this.update();
  }
};


/**
 * Updates gallery.
 */
TagsGallery.prototype.update = function() {
  this.items = this.predefinedItems.concat(this.userItems);

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
    .on('click', function(item, i) {
      var itemElm = d3.select(this);
      itemElm.classed('selected', !itemElm.classed('selected'));
      gallery.onItemClick(item, i);
    })
    .on('mouseover', function(item, i) {
      gallery.onItemFocus(item, i, true);
      d3.select(this).selectAll('img').classed('focus', true);
    })
    .on('mouseout', function(item, i) {
      Utils.hideTooltip();
      d3.select(this).selectAll('img').classed('focus', false);
      gallery.onItemFocus(item, i, false);
    })
    .html(function(item, i) {
      return gallery.getItemButtons(item, i) + gallery.getItemInfo(item, i);
    });

  // Configures actions on images.
  items.each(function(item, i) {
    // Only clickable tags.
    if (item['clickable']) {
      var itemElm = d3.select(this);
      itemElm.selectAll('img').each(function() {
        var img = d3.select(this);
        var actionType = img.attr('actionType');
        img
          .on('mouseover', function() {
            Utils.showTooltip();
          })
          .on('mousemove', function() {
            Utils.updateTooltip(actionType + ' tag "' + item.label + '"');
          })
          .on('mouseout', function() {
            Utils.hideTooltip();
          })
          .on('click', function() {
            gallery.onItemActionClick(item, i, actionType);
            event.stopPropagation();
          });
      });
    }
  });
};


/**
 * Builds html content with info about an item in the gallery.
 */
TagsGallery.prototype.getItemInfo = function(item, i) {
  // TODO Add more details about tag.
  return item.label;

  // TODO(cesar): Add buttons "Tag" / "Untag".
};


/**
 * Builds html content with buttons for labeling relevancy an item in the gallery,
 * such as Yes, No, Maybe.
 */
TagsGallery.prototype.getItemButtons = function(item, i) {
  var w = 12;
  var c = item['clickable'] ? 'clickable' : 'not-clickable';
  return '<img actionType="Remove" src="img/remove.png" width="' + w + 'px" class="' + c + '">'
    + '<img actionType="Apply" src="img/apply.png" width="' + w + 'px" class="' + c + '">';
};


/**
 * Handles click in an item.
 */
TagsGallery.prototype.onItemClick = function(item, i) {
  __sig__.emit(__sig__.tag_clicked, item);
};


/**
 * Handles item focus.
 */
TagsGallery.prototype.onItemFocus = function(item, i, onFocus) {
  __sig__.emit(__sig__.tag_focus, item, onFocus);
};


/**
 * Handles click in an item.
 */
TagsGallery.prototype.onItemActionClick = function(item, i, actionType) {
  __sig__.emit(__sig__.tag_action_clicked, item, actionType);
};
