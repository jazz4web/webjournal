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
    url: '/api/admin-tools',
    headers: tee,
    success: function(data) {
      console.log(data);
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#toolst').html(), data);
        $('#mc').append(html);
        checkPC(860);
      }
    },
    dataType: 'json'
  });
  if (tee) {
    $('body').on('click', '#user-submit', function() {
      $(this).blur();
      let tee = {
        username: $('#username').val(),
        address: $('#address').val(),
        password: $('#password').val(),
        confirma: $('#confirmation').val(),
        auth: window.localStorage.getItem('sestee')
      };
      if (tee.username && tee.address && tee.password && tee.confirma) {
        $.ajax({
          method: 'POST',
          url: '/api/admin-tools',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.assign(data.redirect);
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() { checkPC(860); }, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
  }
  checkPC(860);
});
