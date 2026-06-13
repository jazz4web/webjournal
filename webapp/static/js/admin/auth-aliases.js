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
    url: '/api/admin-auth-aliases',
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
        let html = Mustache.render($('#aliasest').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }
    },
    dataType: 'json'
  });
  if (ses) {
    let url = window.location.pathname + '?page=';
    $('body').on('click', '.page-link', function(event) {
      window.location.assign(url + $(this).text().trim());
    });
    $('body').on('click', '#next-link', {page: page}, function(event) {
      let p = event.data.page + 1;
      window.location.assign(url + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      let p = event.data.page - 1;
      window.location.assign(url + p);
    });
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.remove-button', {page: page}, remAli);
  }
  checkPC(860);
});
