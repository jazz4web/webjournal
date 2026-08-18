$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {}
  $.ajax({
    method: 'GET',
    url: '/api/announce',
    headers: tee,
    data: {
      suffix: suffix
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        $('title').text(
          $('title').text().trim() + ' ' + data.announce.headline);
        let html = Mustache.render($('#announcet').html(), data);
        $('#mc').append(html);
        $('.date-field').each(function() {formatDateTime($(this)); });
        $('#length-marker').text(1024-data.announce.body.length);
        checkPC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
      }
    },
    error: error403,
    dataType: 'json'
  });
  checkPC(860);
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '#remove-button', function() {
      $(this).blur();
      $.ajax({
        method: 'DELETE',
        url: '/api/announce',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          suffix: suffix,
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
    $('body').on('click', '#state-button', function() {
      $(this).blur();
      changeAnn('pub', 0, suffix);
    });
    $('body').on('click', '#text-submit', function() {
      $(this).blur();
      if (!$('#text-editor .form-group-a').hasClass('has-error')) {
        let value = $('#text-edit').val();
        changeAnn('body', value, suffix);
      }
    });
    $('body').on('blur', '#text-edit', blurBodyAn);
    $('body').on(
      'keyup', '#text-edit',
      {len:1024, marker:'#length-marker', block:'.length-marker'},
      trackMarker);
    $('body').on('click', '#headline-submit', function() {
      $(this).blur();
      let value = $('#headline').val();
      if (!$('.input-field').hasClass('has-error')) {
        changeAnn('headline', value, suffix);
      }
    });
    $('body').on('keyup', '#headline', function(event) {
      if (event.which == 13) $('#headline-submit').trigger('click');
    });
    $('body').on(
      'keyup blur', '#headline',
      {min:3, max:50, block:'.input-field'}, markInputError);
    $('body').on('click', '#trash-button', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#remove-button-form').slideDown('fast', function() {
          $('.editor-forms-block').slideDown(
            'slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#remove-button-form').is(':hidden')) {
          let f = $('#remove-button-form');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#remove-button-form').slideUp('fast');
            checkPC(860);
          });
        }
      }
    });
    $('body').on('click', '#edit-headline', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#headline-editor').slideDown('fast', function() {
          $('.editor-forms-block').slideDown(
            'slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#headline-editor').is(':hidden')) {
          let f = $('#headline-editor');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#headline-editor').slideUp('fast');
            checkPC(860);
          });
        }
      }
    });
    $('body').on('click', '#edit-text-button', function() {
      $(this).blur();
      if ($('.editor-forms-block').is(':hidden')) {
        $('#text-editor').slideDown('fast', function() {
          $('.editor-forms-block').slideDown(
            'slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        });
      } else {
        if ($('#text-editor').is(':hidden')) {
          let f = $('#text-editor');
          f.siblings().each(function() {
            $(this).slideUp('slow');
          });
          f.slideDown('slow', function() {checkPC(860);});
          scrollPanel($('.editor-forms-block'));
        } else {
          $('.editor-forms-block').slideUp('slow', function() {
            $('#text-editor').slideUp('fast');
            checkPC(860);
          });
        }
      }
    });
    $('body').on('click', '#go-home', function() {
      $(this).blur();
      window.location.assign('/announces/');
    });
    $('body').on('click', '.entity-text-block img', clickImage);
  }
});
