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
    url: '/api/comments',
    headers: tee,
    data: {
      page: page
    },
    success: function(data) {
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#commentst').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() {formatDateTime($(this)); });
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
  checkPC(860);
  if (ses) {
    $('body').on('click', '.remove-button', function() {
      $(this).blur();
      let par = $(this).parents('.entity-block');
      $.ajax({
        method: 'DELETE',
        url: '/api/comment',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          cid: $(this).data().id
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
            $('#ealert').addClass('next-block');
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.checked-button', function() {
      $(this).blur();
      let par = $(this).parents('.entity-block');
      $.ajax({
        method: 'PUT',
        url: '/api/comment',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          id: $(this).data().id,
          auth: window.localStorage.getItem('sestee')
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/comments/');
          } else {
            showError(par, data);
            $('#ealert').addClass('next-block');
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.link-button', function() {
      $(this).blur();
      window.open($(this).data().art, '_blank');
    });
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
  }
});
