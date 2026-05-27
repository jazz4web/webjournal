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
    url: '/api/profile',
    headers: tee,
    data: {
      username: username
    },
    success: function(data) {
      console.log(data)
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#mc').append(html);
        checkPC(860);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        if ($('#select-group').length) {
          let s = $('#select-group option');
          for (let n = 0; n < s.length; n++) {
            if (s[n].value == data.user.group) {
              $(s[n]).attr('selected', 'selected');
            }
          }
        }
      }
    },
    dataType: 'json'
  });
  checkPC(860);
});
