$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showLabeledDrafts('/api/alabels', page, label, ses);
  $('body').on('click', '.alias-link', function() {
    $(this).blur();
    window.location.assign($(this).data().link);
  });
  $('body').on('click', '.page-link', linkPage);
  $('body').on('click', '#next-link', {page:page}, linkNext);
  $('body').on('click', '#prev-link', {page:page}, linkPrev);
  checkPC(860);
  setTimeout(setCookies, 900);
});
