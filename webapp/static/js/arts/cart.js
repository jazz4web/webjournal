$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  checkAuth(ses);
  $('body').on('click', '.closeable', closeTopFlashed);
  showArt('/api/cart', slug, ses);
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.copy-link', showCopyForm);
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '#move-screen-up', function() {
      $(this).blur();
      scrollPanel($('#navigation'));
    });
    $('body').on('click', '#censor-this', {slug:slug}, censorThis);
  }
  checkPC(860);
});
