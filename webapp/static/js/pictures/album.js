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
        checkSelector('#select-status option', data.album.state);
        if (data.pv) renderPV(data.pagination.page);
        $('.items-row-block').each(function() {
          if (!$(this).next().length) $(this).removeClass('bordered');
        });
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '.remove-album', function() {
      $(this).blur();
      let suffix = $(this).data().suffix;
      $.ajax({
        method: 'DELETE',
        url: '/api/pictures',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          suffix: suffix
        },
        success: function(data) {
          if (data.done) {
            window.location.replace('/pictures/');
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on(
        'click', '#rem-pic-button', {page:page, suffix:suffix},
        function(event) {
      $(this).blur();
      let p = ($('.album-header-panel').length > 1) ?
        event.data.page : event.data.page - 1;
      let suffix = $(this).data().suffix;
      $.ajax({
        method: 'DELETE',
        url: '/api/pictures/' + event.data.suffix,
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          picture: suffix,
          page: p
        },
        success: function(data) {
          if (data.url) {
            window.location.replace(data.url);
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() {checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', function() {
      $(this).blur();
      let rf = $('#remove-form');
      let lf = $('#link-form');
      let mf = $('#md-form');
      if (rf.is(':hidden')) {
        rf.slideDown('slow', function() { checkPC(860); });
        mf.slideUp('slow', function() { checkPC(860); });
        lf.slideUp('slow', function() { checkPC(860); });
      } else {
        rf.slideUp('slow', function() { checkPC(860); });
      }
    });
    $('body').on('click', '.copy-link', function() {
      $(this).blur();
      let lf = $('#link-form');
      let mf = $('#md-form');
      let rf = $('#remove-form');
      if (lf.is(':hidden')) {
        lf.slideDown('slow', function() { checkPC(860); });
        mf.slideUp('slow', function() { checkPC(860); });
        rf.slideUp('slow', function() { checkPC(860); });
      } else {
        lf.slideUp('slow', function() { checkPC(860); });
      }
    });
    $('body').on('click', '.copy-md-code', function() {
      $(this).blur();
      let mf = $('#md-form');
      let lf = $('#link-form');
      let rf = $('#remove-form');
      if (mf.is(':hidden')) {
        mf.slideDown('slow', function() { checkPC(860); });
        lf.slideUp('slow', function() { checkPC(860); });
        rf.slideUp('slow', function() { checkPC(860); });
      } else {
        mf.slideUp('slow', function() { checkPC(860); });
      }
    });
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let elem = $(this);
        let form = $('#create-form-block');
        if (!form.is(':hidden')) form.slideUp('slow');
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
        }
        elem.addClass('clicked-item');
        let tee = ses ? {
          'x-br-ses': ses,
          'x-auth-sestee': window.localStorage.getItem('sestee')
        } : {};
        $.ajax({
          method: 'GET',
          url: '/api/picstat',
          headers: tee,
          data: {
            suffix: elem.data().suffix
          },
          success: function(data) {
            if (data.picture) {
              let sb = $('.pic-stat-block');
              if (sb.length) {
                $('.item-date-field').removeClass('item-date-field');
                $('.pb').removeClass('pb');
                sb.slideUp('slow', function() { sb.remove(); });
              }
              let html = Mustache.render($('#picturet').html(), data);
              elem.after(html);
              let bw = parseInt($('.clicked-item').width());
              let pw = parseInt($('.pb').attr('width'));
              if (pw >= bw - 24) {
                let ph = parseInt($('.pb').attr('height'));
                let w = bw - 24;
                let h = Math.round(ph / (pw / w));
                $('.pb').attr({ "width": w, "height": h });
              }
              $('.pic-stat-block').slideDown('slow', function() {
                scrollPanel($('.clicked-item'));
                checkPC(860);
              });
              formatDateTime($('.item-date-field'));
              $('#copy-button').on('click', {cls:'.album-form'}, copyThis);
              $('#copy-button-b').on('click', {cls:'.album-form'}, copyThis);
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() { checkPC(860); }, 400);
            }
          },
          error: error403,
          dataType: 'json'
        });
      } else {
        let elem = $(this);
        let sb = $('.pic-stat-block');
        sb.slideUp('slow', function() {
          sb.remove();
          elem.removeClass('clicked-item');
          checkPC(860);
        });
      }
    });
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
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          let sb = $('.pic-stat-block');
          sb.slideUp('slow', function() {
            sb.remove();
            checkPC(860);
          });
        }
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
    $('body').on('change', '#select-status', {suffix:suffix}, changeStatus);
    $('body').on('click', '.show-state-form', showStateForm);
    $('body').on('click', '#show-rename-form', showRenameForm);
    $('body').on('click', '#rename-album', {suffix: suffix}, renameAlbum);
    $('body').on(
      'keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'},
      markInputError);
    $('body').on('keyup', '#title-change', function(event) {
      if (event.which === 13) $('#rename-album').trigger('click');
    });
    $('body').on('click', '.show-rename-form', showRenameForm);
  }
});
