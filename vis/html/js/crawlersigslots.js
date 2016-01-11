/**
 * @fileoverview Manager for signal slots throught the application.
 * Refer to this when creating new signals, and to connect slots.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages signal slots for application UI.
 */
var SigSlots = (function() {
  ////// Signals definition is centralized here.
  __sig__.available_crawlers_list_loaded = function(crawlers) {};
  __sig__.available_crawlers_list_reloaded = function(crawlers) {};
  __sig__.available_proj_alg_list_loaded = function(proj_alg) {};
  __sig__.new_pages_summary_fetched = function(summary, isFilter) {};
  __sig__.previous_pages_summary_fetched = function(summary, isFilter) {};
  __sig__.terms_summary_fetched = function(summary) {};
  __sig__.term_focus = function(term, onFocus) {};
  __sig__.term_toggle = function(term, shiftClick) {};
  __sig__.terms_snippets_loaded = function(snippetsData) {};
  __sig__.pages_loaded = function(pages) {};
  __sig__.queries_loaded = function(queries) {};
  __sig__.tag_focus = function(tag, onFocus) {};
  __sig__.tag_clicked = function(tag) {};
  __sig__.tag_action_clicked = function(tag, actionType, pages, refresh_plot) {};
  __sig__.tag_individual_page_action_clicked = function(tag, actionType, page) {};
  __sig__.brushed_pages_changed = function(pagesIndices) {};

  __sig__.add_crawler = function(index_name) {};
  __sig__.query_enter = function(terms) {};
  __sig__.filter_enter = function(terms) {};
  __sig__.add_term = function(term) {};
  __sig__.add_neg_term = function(term) {};
  __sig__.delete_term = function(term) {};
  __sig__.load_new_pages_summary = function(isFilter) {};

  __sig__.bokeh_get_session = function() {};
  __sig__.bokeh_insert_plot = function() {};

  //__sig__.pages_labels_changed = function() {};
  //__sig__.term_selected = function(term) {};
  //__sig__.query_enter = function(query) {};
  //__sig__.pages_do_ranking = function() {};
  //__sig__.pages_extract_terms = function() {};
  //__sig__.brushed_pages_changed = function(pagesIndices) {};
  //__sig__.add_term_to_query_box = function(term) {};

  var pub = {};
  ////// CONNECTS SIGNALS TO SLOTS
  // e.g. SigSlots.connect(__sig__.eventHappened, myObject, myObject.onEventHappened);
  pub.connect = function(
      signal, slotInstance, slotMethod) {
    __sig__.connect(
      __sig__, signal,
      slotInstance, slotMethod);
  };
  return pub;
}());
