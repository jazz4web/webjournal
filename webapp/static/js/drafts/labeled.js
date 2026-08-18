$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showLabeledDrafts('/api/labels', page, label, ses);
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.alias-link', function(event) {
      $(this).blur();
    });
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
    $('body').on('click', '.page-link', linkPage);
  }
  checkPC(860);
});
