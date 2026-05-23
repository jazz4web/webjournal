function slidePage(eid) {
  let block = $(eid);
  block.slideDown('slow', function() { checkPC(860); });
  block.siblings().each(function() {
    $(this).slideUp('slow', function() { $(this).remove(); });
  });
}
