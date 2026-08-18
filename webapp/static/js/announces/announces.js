$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter()
  $('body').on('click', '.closeable', closeTopFlashed);
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {};
  $.ajax({
    method: 'GET',
    url: '/api/announces',
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
        let html = Mustache.render($('#announcest').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('click', '#submit', function() {
      $(this).blur();
      $('#headline').trigger('blur');
      $('#body').trigger('blur');
      if (!$('.form-group-a').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/announces',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            title: $('#headline').val(),
            text: $('#body').val(),
            heap: $('#heap').is(':checked') ? 1 : 0,
            auth: window.localStorage.getItem('sestee')
          },
          success: function(data) {
            if (data.announce) {
              window.location.assign(data.announce);
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
              setTimeout(function() {checkPC(860); }, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '.slidable', function() {
      let b = $(this).siblings('.block-body');
      if (b.is(':hidden')) {
        b.slideDown('slow', function() {
          scrollPanel($('#new-title'));
          checkPC(860);
        });
      } else {
        b.slideUp('slow', function() {checkPC(860); });
      }
    });
    $('body').on('blur', '#body', blurBodyAn);
    $('body').on(
      'keyup blur', '#headline',
      {min:3, max:50, block:'.form-group-a'}, markInputError);
    $('body').on(
      'keyup', '#body',
      {len: 1024, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
  }
});
