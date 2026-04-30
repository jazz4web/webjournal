$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  checkPC(860);
});
