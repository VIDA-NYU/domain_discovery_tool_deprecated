var data_table_ids = ['urls', 'tlds'];

var add_interactor_listener = function() {
  $('.grid-canvas').click(function() {
    setTimeout(function() { //pbly poor way to wait for class change
      var global_state = {};
      for (i=0; i<data_table_ids.length; i++) {
        global_state[data_table_ids[i]] = get_table_state(data_table_ids[i]);
      }
      $.ajax({
        type: "POST",
        url: '/update_cross_filter_plots' + window.location.search, //ehh not great
        data: JSON.stringify(global_state),
        contentType: "application/json",
        dataType: "json",
        success: function() {
          console.log('request sent');
        }
      });
    }, 10);
  });
};

var get_table_state = function(id) {
  var current = $("#".concat(id)).find(".bk-slick-cell.l0.selected");
  var active_cells = [];
  for (j = 0; j < current.length; j++) {
    active_cells.push(current[j].innerText);
  }
  return active_cells;
};

$(document).ready(function() {
  console.log('page is ready');
  setTimeout(add_interactor_listener, 100); //will fix
});
