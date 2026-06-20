function showStateForm() {
  $(this).blur();
  let ren = $('#rename-form');
  let stch = $('#change-status-form');
  if (stch.is(':hidden')) {
    stch.slideDown('slow', function() { checkPC(860); });
    ren.slideUp('slow', function() { checkPC(860); });
  } else {
    stch.slideUp('slow', function() { checkPC(860); });
  }
}
