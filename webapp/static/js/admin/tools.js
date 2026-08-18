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
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#toolst').html(), data);
        $('#mc').append(html);
        checkPC(860);
        checkSelector('#select-group option', data.dgroup);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (ses) {
    checkIncomming(ses);
    $('body').on('click', '#li-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/setcounter',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          value: $('#li-edit').val()
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
    });
    $('body').on('click', '#ipage-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/chindex',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          value: $('#ipage-suffix').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/');
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() {checkPC(860);}, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#robots-submit', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/chrobots',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          value: $('#reditor').val()
        },
        success: function(data) {
          if (data.done) {
            window.location.assign('/robots.txt');
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() {checkPC(860);}, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#edit-li-stat', function() {
      $(this).blur();
      let l = $('#li-editor');
      if (l.is(':hidden')) {
        l.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        l.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-index', function() {
      $(this).blur();
      let i = $('#index-editor');
      if (i.is(':hidden')) {
        i.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        i.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-robots', function() {
      $(this).blur();
      let r = $('#robots-editor');
      if (r.is(':hidden')) {
        r.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        r.slideDown('slow');
      }
    });
    $('body').on('click', '#edit-perms', function() {
      $(this).blur();
      let p = $('#default-perms-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
    $('body').on('click', '#create-user', function() {
      $(this).blur();
      let p = $('#new-user-editor');
      if (p.is(':hidden')) {
        p.siblings().each(function() {
          if (!$(this).is(':hidden')) $(this).slideUp('slow');
        });
        p.slideDown('slow');
      }
    });
    $('body').on('change', '#select-group', function() {
      let res = $(this).val();
      $.ajax({
        method: 'PUT',
        url: '/api/chdg',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          dgroup: res,
          auth: window.localStorage.getItem('sestee')
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
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
