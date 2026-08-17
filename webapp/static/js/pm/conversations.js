$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {};
  $.ajax({
    method: 'GET',
    url: '/api/convs',
    headers: tee,
    data: {
      page: page
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#convst').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() {formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
  }
  checkPC(860);
});
