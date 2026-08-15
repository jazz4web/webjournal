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
    url: '/api/conv',
    headers: tee,
    data: {
      username: username,
      page: page,
      nopage: nopage
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#convt').html(), data);
        $('#mc').append(html);
        if ($('.today-field').legnth) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.incomming) scrollPanel($('.last-pm'));
        if (!data.pagination.next && data.pagination.messages) {
          for (let i = 0; i < data.pagination.messages.length; i++) {
            let message = data.pagination.messages[i];
            if (i == data.pagination.messages.length - 1) {
              html = '<button type="button"' +
                     '        title="обновить страницу"' +
                     '        class="btn-sm btn-default reload-button">' +
                     '  <span class="glyphicon glyphicon-refresh"' +
                     '        aria-hidden="true"></span>' +
                     '</button>';
              $('.last-pm .pm-options').append(html);
              if (message.author_username == data.cu.username) {
                if (message.received) {
                  html = '<button type="button"' +
                         '        title="новое сообщение"' +
                         '    class="btn-sm btn-primary new-pm-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                } else {
                  html = '<button type="button"' +
                         '        title="редактировать"' +
                         '        data-id="' + message.id + '"' +
                         '        class="btn-sm btn-danger edit-button">' +
                    '<span class="glyphicon glyphicon-edit"' +
                    '      aria-hidden="true"></span>' +
                         '</button>';
                  $('.last-pm .pm-options').prepend(html);
                };
              } else {
                html = '<button type="button"' +
                       '        title="ответить"' +
                       '    class="btn-sm btn-primary new-pm-button">' +
                  '<span class="glyphicon glyphicon-edit"' +
                  '      aria-hidden="true"></span>' +
                       '</button>';
                $('.last-pm .pm-options').prepend(html);
              }
            }
          }
        }
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
        if (!parseInt(nopage)) {
          page = parseInt($('.entity-pagination .page-current').text());
        }
        $('body').on('click', '#prev-link', {page:page}, linkPrev);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let mid = $(this).data().id;
      let p = 1;
      if ($('.entity-pagination').length) {
        p = parseInt($('.entity-pagination .page-current').text());
      }
      $.ajax({
        method: 'DELETE',
        url: '/api/conv',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          page: p,
          mid: mid,
          last: $('.pm-block').length,
          auth: window.localStorage.getItem('sestee')
        },
        success: function(data) {
          if (data.done) {
            window.location.replace(data.redirect);
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() {checkPC(860);}, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page: page}, linkNext);
    $('body').on('click', '#pm-editor-submit', function() {
      $(this).blur();
      let val = $('#pm-editor-edit').val();
      let mid = $(this).data().id;
      if (val) {
        $.ajax({
          method: 'PATCH',
          url: '/api/conv',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            text: val,
            mid: mid,
            auth: window.localStorage.getItem('sestee')
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#edit-message', data);
              $('#ealert').addClass('next-block');
              scrollPanel($('#ealert'));
              setTimeout(function() {checkPC(860);}, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#cancel-edit', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '.edit-button', function() {
      $(this).blur();
      if (!$('#edit-message').length) {
        $.ajax({
          method: 'PUT',
          url: '/api/conv',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            auth: window.localStorage.getItem('sestee'),
            mid: $(this).data().id
          },
          success: function(data) {
            if (data.done) {
              if (data.update) window.location.reload();
              if (data.text) {
                let html = Mustache.render($('#editpmt').html(), data);
                $('.last-pm').after(html);
                $('#edit-message').slideDown('slow', function() {
                  scrollPanel($('#edit-message'));
                });
                if ($('.today-field').length) {
                  renderTF('.today-field', luxon.DateTime.now());
                }
              }
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() {checkPC(860);}, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.new-pm-button', function() {
      $(this).blur();
      let fblock = $('#new-message');
      if (fblock.is(':hidden')) {
        fblock.slideDown('slow', function() {
          scrollPanel($('.last-pm'));
          checkPC(860);
        });
      } else {
        fblock.slideUp('slow', function() {
          checkPC(860);
        });
      }
    });
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.reload-button', function() {
      $(this).blur();
      window.location.reload();
    });
    $('body').on('click', '#pm-submit', function() {
      $(this).blur();
      let text = $('#pm-editor').val();
      if (text) {
        $.ajax({
          method: 'POST',
          url: '/api/conv',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            recipient: username,
            auth: window.localStorage.getItem('sestee'),
            message: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() {checkPC(860);}, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
  }
  checkPC(860);
});
