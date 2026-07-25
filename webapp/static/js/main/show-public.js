$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  countClicks(suffix);
  $('.date-field').each(function() { formatDateTime($(this)); });
  $('.copy-link').on('click', showCopyForm);
  $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
  checkPC(860);
  $('.entity-text-block iframe').each(adjustFrame);
  $('.entity-text-block').children().each(setMargin);
  $('.entity-text-block img').each(adjustImage);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('#get-more').on('click', function() {
    $(this).blur();
    window.location.assign($(this).data().link);
  });
  setTimeout(setCookies, 900);
  pingUser(300000, 12);
});
