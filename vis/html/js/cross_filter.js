var button_group_tags = ['tags', 'tlds'];

var add_interactor_listener = function() {
  $(".bk-bs-btn-group").on('click', function() {
    setTimeout(function() { //pbly poor way to wait for class change
      var global_state = {};
      for (i=0; i<button_group_tags.length; i++) {
        global_state[button_group_tags[i]] = get_button_group_state(button_group_tags[i]);
      }
      $.ajax({
        url: '/update_cross_filter_plots',
        data: global_state,
        success: function() {
          console.log('request sent');
        }
      });
      console.log(global_state);
    }, 10);
  });
};

var get_button_group_state = function(id) {
  var current = $("#".concat(id)).find(".bk-bs-active").children();
  var active_buttons = [];
  for (j = 0; j < current.length; j++) {
    active_buttons.push(current[j].value);
  }
  return active_buttons;
};

$(document).ready(function() {
  console.log('page is ready');
  add_interactor_listener();
});
