$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showDrafts('/api/carts', page, ses);
  checkPC(860);
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.alias-link', function(event) {
      $(this).blur();
    });
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
  }
});
