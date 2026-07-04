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
    url: '/api/aliases',
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
        let html = Mustache.render($('#aliasest').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.entity-block').each(checkNext);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.copy-button').on('click', copyAlias);
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    $('body').on('click', '.remove-button', {page: page}, function(event) {
      $(this).blur();
      let p = ($('.remove-button').length > 1) ?
        event.data.page : event.data.page - 1;
      let suffix = $(this).data().suffix;
      $.ajax({
        method: 'DELETE',
        url: '/api/aliases',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          suffix: suffix,
          page: p,
          auth: window.localStorage.getItem('sestee')
        },
        success: function(data) {
          if (data.done) {
            window.location.replace(data.url);
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '#next-link', {page: page}, linkNext);
    $('body').on('click', '#prev-link', {page: page}, linkPrev);
    $('body').on('keyup', '#link', function(event) {
      if (event.which == 13) $('#link-submit').trigger('click');
    });
    $('body').on('click', '#link-submit', function() {
      $(this).blur();
      let link = $('#link').val();
      if (link.startsWith('https://') || link.startsWith('http://')) {
        $.ajax({
          method: 'POST',
          url: '/api/aliases',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            link: link,
            auth: window.localStorage.getItem('sestee')
          },
          success: function(data) {
            if (data.done) {
              if (data.alias) {
                $('.found-alias').remove();
                let html = Mustache.render($('#aliast').html(), data.alias);
                $('#new-title').after(html);
                formatDateTime($('.found-alias .date-field'));
                $('#link').val('');
                let b = '#alias-' + data.alias.suffix;
                $(b).on('click', copyAlias);
                checkPC(860);
              } else {
                window.location.reload();
              }
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
