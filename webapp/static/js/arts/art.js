$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  checkAuth(ses);
  $('body').on('click', '.closeable', closeTopFlashed);
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  showArt('/api/art', slug, ses);
  pingUser(300000, 12);
  if (ses) {
    $('body').on('click', '#editor-button', function() {
      $(this).blur();
      window.location.assign($(this).data().link);
    });
  }
  checkPC(860);
  setTimeout(setCookies, 900);
});
