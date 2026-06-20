function showRenameForm() {
  $(this).blur();
  let ren = $('#rename-form');
  let stch = $('#change-status-form');
  if (ren.is(':hidden')) {
    ren.slideDown('slow', function() { checkPC(860); });
    stch.slideUp('slow', function() { checkPC(860); });
  } else {
    ren.slideUp('slow', function() { checkPC(860);});
  }
}
