$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')} : {};
  $.ajax({
    method: 'GET',
    url: '/api/people',
    headers: tee,
    data: {
      page: page
    },
    success: function(data) {
      console.log(data);
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#peoplet').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.last-seen').each(function() { renderLastSeen($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }
    },
    dataType: 'json'
  });
  $('body').on('click', '#next-link', {page: page}, function(event) {
    let p = event.data.page + 1;
    window.location.assign(
      window.location.pathname + '?page=' + p);
  });
  $('body').on('click', '#prev-link', {page: page}, function(event) {
    let p = event.data.page - 1;
    window.location.assign(
      window.location.pathname + '?page=' + p);
  });
  $('body').on('click', '.page-link', function(event) {
    window.location.assign(
      window.location.pathname + '?page=' + $(this).text().trim());
  });
  checkPC(860);
  setTimeout(setCookies, 900);
});
