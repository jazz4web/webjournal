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
    url: '/api/admin-auth-pictures',
    headers: tee,
    data: {
      page: page,
      author: author
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#picturest').html(), data);
        $('#mc').append(html);
        $('.entity-block').each(checkNext);
        setTimeout(function() {
          checkPC(860);
          $('.picture-body img').each(adjustImage);
        }, 100);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.remove-button', {page:page}, remPic);
  }
  checkPC(860);
});
