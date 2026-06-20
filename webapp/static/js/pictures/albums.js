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
    url: '/api/pictures',
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
        let html = Mustache.render($('#albumst').html(), data);
        $('#mc').append(html);
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#statistic-block').append(ust);
        if (data.pagination && data.extra) {
          $('#create-form-block').addClass('hidden');
        }
        if($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        formatDateTime($('.date-field'));
        checkPC(860);
        let pub = $('#pub-f');
        pub.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#priv-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#priv-f');
          }
        });
        let priv = $('#priv-f');
        priv.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#ffo-f');
          } else {
            checkBox('#pub-f');
          }
        });
        let ffo = $('#ffo-f');
        ffo.on('change', function() {
          if ($(this).is(':checked')) {
            uncheckBox('#pub-f');
            uncheckBox('#priv-f');
          } else {
            checkBox('#pub-f');
          }
        });
        if (data.pv) renderPV(data.pagination.page);
        $('.items-row-block').each(function() {
          if (!$(this).next().length) $(this).removeClass('bordered');
        });
      }
    },
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '#album-first-page', function() {
      $(this).blur();
      window.location.assign('/pictures/');
    });
    $('body').on('click', '.show-album', function() {
      $(this).blur();
      let url = '/pictures/' + $(this).data().dest;
      window.location.assign(url);
    });
    $('body').on('click', '.show-state-form', showStateForm);
    $('body').on('click', '.show-rename-form', showRenameForm);
    $('body').on('click', '.album-header-panel', function() {
      if (!$(this).hasClass('clicked-item')) {
        let cform = $('#create-form-block');
        let fform = $('#find-pic-block');
        if (!cform.is(':hidden')) cform.slideUp('slow');
        if (!fform.is(':hidden')) fform.slideUp('slow');
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
        }
        let elem = $(this);
        showAlbumStat(elem, ses);
      } else {
        let sb = $('.stat-block');
        let th = $(this);
        sb.slideUp('slow', function() {
          sb.remove();
          th.removeClass('clicked-item');
        });
      }
    });
    $('body').on('click', '#create-new', function() {
      $(this).blur();
      if (!$('#title-group').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/pictures',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            auth: window.localStorage.getItem('sestee'),
            title: $('#title').val(),
            state: $('#create-form-block :checked').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.assign(data.target);
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('keyup', '#title', function(event) {
      if (event.which === 13) $('#create-new').trigger('click');
    });
    $('body').on(
      'keyup blur', '#title', {min: 3, max: 100, block: '.form-group'},
      markInputError);
    $('body').on('click', '#create-new-album', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fblock = $('#find-pic-block');
      if (cform.is(':hidden')) {
        if (!fblock.is(':hidden')) fblock.slideUp('slow');
        cform.slideDown('slow', function() {
          if (!fblock.is(':hidden')) fblock.slideUp('slow');
          $('#title').focus();
          checkPC(860);
        });
        scrollPanel($('#albums-block'));
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          let sb = $('.stat-block');
          sb.slideUp('slow', function() {
            sb.remove();
          });
        }
      } else {
        cform.slideUp('slow', function() { checkPC(860); });
      }
    });
    $('body').on('click', '#album-search', function() {
      $(this).blur();
      let cform = $('#create-form-block');
      let fblock = $('#find-pic-block');
      if (fblock.is(':hidden')) {
        if (!cform.is(':hidden')) cform.slideUp('slow');
        fblock.slideDown('slow', function() {
          scrollPanel($('#albums-block'));
          checkPC(860);
          $('#find-input').focus();
        });
        if ($('.clicked-item').length) {
          $('.clicked-item').removeClass('clicked-item');
          let sb = $('.stat-block');
          sb.slideUp('slow', function() {
            sb.remove();
          });
        }
      } else {
        fblock.slideUp('slow', function() {
          checkPC(860);
        });
      }
    });
    $('body').on('click', '#album-reload', reload);
    $('body').on('click', '#next-link', {page: page}, function(event) {
      let p = event.data.page + 1;
      window.location.assign('/pictures/?page=' + p);
    });
    $('body').on('click', '#prev-link', {page: page}, function(event) {
      let p = event.data.page - 1;
      window.location.assign('/pictures/?page=' + p);
    });
    $('body').on('click', '.page-link', function(event) {
      window.location.assign('/pictures/?page=' + $(this).text().trim());
    });
  }
  checkPC(860);
});
