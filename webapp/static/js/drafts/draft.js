$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showDraft(slug);
  if (ses) {
    $('body').on('click', '.copy-link', showCopyForm);
  }
  checkPC(860);
});
