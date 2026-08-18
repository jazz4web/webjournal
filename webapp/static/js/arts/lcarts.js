$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showLabeledDrafts('/api/lcarts', page, label, ses);
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.alias-link', function(event) {
      $(this).blur();
    });
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
  }
  checkPC(860);
});
