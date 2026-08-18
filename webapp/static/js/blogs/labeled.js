$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {
    'x-auth-sestee': 'empty'
  };
  $.ajax({
    method: 'GET',
    url: '/api/lblog',
    headers: tee,
    data: {
      page: page,
      username: username,
      label: label
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftst').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() {formatDateTime($(this));});
        $('.labels').each(fixComma);
        if (data.pv) renderPV(data.pagination.page);
        setTimeout(function() {checkPC(860);}, 400);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) checkIncomming(ses);
  checkPC(860);
  $('body').on('click', '.alias-link', function() {
    $(this).blur();
    window.location.assign($(this).data().link);
  });
  $('body').on('click', '.page-link', linkPage);
  $('body').on('click', '#next-link', {page:page}, linkNext);
  $('body').on('click', '#prev-link', {page:page}, linkPrev);
  setTimeout(setCookies, 900);
});
