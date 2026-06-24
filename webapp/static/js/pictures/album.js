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
    url: '/api/pictures/' + suffix,
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
        let html = Mustache.render($('#albumt').html(), data);
        $('#mc').append(html);
        let ast = Mustache.render($('#astatt').html(), data);
        $('#statistic-block').append(ast);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        formatDateTime($('.date-field'));
        checkSelector(data.album.state);
        if (data.pv) renderPV(data.pagination.page);
        $('.items-row-block').each(function() {
          if (!$(this).next().length) $(this).removeClass('bordered');
        });
        checkPC(860);
      }
    },
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '#album-first-page', function() {
      $(this).blur();
      window.location.assign(window.location.pathname);
    });
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
    $('body').on('click', '#upload-new', {suffix:suffix}, function(event) {
      $(this).blur();
      let upblock = $('#create-form-block');
      if (!upblock.is(':hidden')) {
        upblock.slideUp('slow', function() { checkPC(860); });
      } else {
        upblock.slideDown('slow', function() { checkPC(860); });
        scrollPanel($('#album-block'));
      }
    });
    $('body').on('click', '#go-home', function() {
      $(this).blur();
      window.location.assign('/pictures/');
    });
    $('body').on('click', '#album-reload', reload);
    $('body').on('change', '#image', {suffix:suffix}, function(event) {
      $('#create-form-block').slideUp('slow', function() {
        $('#progress-block').slideDown('slow');
      });
      let file = $(this)[0].files[0];
      if (file.size <= 5 * 1024 * 1024) {
        let fd = new FormData($('#uploadform')[0]);
        fd.append('auth', window.localStorage.getItem('sestee'));
        $.ajax({
          method: 'POST',
          url: '/api/pictures/' + event.data.suffix,
          processData: false,
          contentType: false,
          cache: false,
          data: fd,
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              if ($('.top-flashed-block').length) {
                $('.top-flashed-block').remove();
              }
              showError('#mc', data);
              scrollPanel($('#ealert'));
              $('#create-form-block').slideDown('slow', function() {
                $('#progress-block').slideUp('slow', function() {
                  checkPC(860);
                });
              });
            }
          },
          dataType: 'json'
        });
      } else {
        let d = {message: 'Недопустимый размер файла.'};
        if ($('.top-flashed-block').length) $('.top-flashed-block').remove();
        showError('#mc', d);
        $('#create-form-block').slideDown('slow', function() {
          $('#progress-block').slideUp('slow', function() { checkPC(860); });
          scrollPanel($('#ealert'));
        });
      }
    });
    $('body').on('click', '.show-state-form', showStateForm);
    $('body').on('click', '.show-rename-form', showRenameForm);
  }
});
