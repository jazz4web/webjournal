$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  checkAuth(ses);
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {
    'x-auth-sestee': 'empty'
  };
  $.ajax({
    method: 'GET',
    url: '/api/blogs',
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
        let html = Mustache.render($('#authorst').html(), data);
        $('#mc').append(html);
        if (!data.cu) {
          let mess = Mustache.render($('#messaget').html(), data);
          $('#mc').before(mess);
        }
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }

    },
    error: error403,
    dataType: 'json'
  });
  if (ses) checkIncomming(ses);
  checkPC(860);
  $('body').on('click', '#next-link', {page:page}, linkNext);
  $('body').on('click', '#prev-link', {page:page}, linkPrev);
  $('body').on('click', '.page-link', linkPage);
  setTimeout(setCookies, 900);
});
