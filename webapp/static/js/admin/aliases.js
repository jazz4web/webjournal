$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  checkPermissions(ses);
  if (ses) {
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.remove-button', {page: 1}, remAli);
    $('body').on('keyup', '#username', function(event) {
      if (event.which == 13) $('#username-submit').trigger('click');
    });
    $('body').on('click', '#username-submit', function() {
      $(this).blur();
      let username = $('#username').val();
      if (username.length > 3) {
        $.ajax({
          method: 'PUT',
          url: '/api/admin-aliases',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            username: username,
            auth: window.localStorage.getItem('sestee')
          },
          success: function(data) {
            if (data.redirect) {
              window.location.assign(data.redirect);
            } else {
              $('#alias').remove();
              $('#suffix').val('');
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() { checkPC(860); }, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('keyup', '#suffix', function(event) {
      if (event.which == 13) $('#suffix-submit').trigger('click');
    });
    $('body').on('click', '#suffix-submit', function() {
      $(this).blur();
      let link = $('#suffix').val();
      if (link.length >= 6) {
        $.ajax({
          method: 'POST',
          url: '/api/admin-aliases',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            link: link,
            auth: window.localStorage.getItem('sestee')
          },
          success: function(data) {
            if (data.alias) {
              $('#ealert').remove();
              $('#alias').remove();
              let html = Mustache.render($('#aliast').html(), data.alias);
              $('#mc').append(html);
              $('#suffix').val('');
              $('#username').val('');
              $('.date-field').each(function() { formatDateTime($(this)); });
            } else {
              $('#alias').remove();
              $('#username').val('');
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() { checkPC(860);}, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
  }
  checkPC(860);
});
