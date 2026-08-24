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
    url: '/api/profile',
    headers: tee,
    data: {
      username: username
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#mc').append(html);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.relation').each(fixComma);
        if (!data.user.description) {
          $('#length-marker').text(500);
        } else {
          $('#length-marker').text(500 - data.user.description.length);
        }
        if ($('#select-group').length) {
          checkSelector('#select-group option', data.user.group);
        }
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
  if (window.localStorage.getItem('sestee')) {
    $('body').on('click', '#pm-message', function() {
      $(this).blur();
      window.location.assign($(this).data().url);
    });
    $('body').on('click', '#blocking-button', function() {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/people',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          uid: $(this).data().uid
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
    $('body').on('click', '#make-friend', function() {
      $(this).blur();
      $.ajax({
        method: 'POST',
        url: '/api/people',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          uid: $(this).data().uid
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
    $('body').on('change', '#select-group', function() {
      let res = $(this).val();
      $.ajax({
        method: 'POST',
        url: '/api/profile',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          group: res,
          username: username,
          auth: window.localStorage.getItem('sestee')
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860);}, 400);
          }
        },
        dataType: 'json'
      });
    });
  }
  if (cu === username ) {
    $('body').on('click', '#chaddress-submit', function() {
      $(this).blur();
      let tee = {
        address: $('#chaddress').val(),
        passwd: $('#chapasswd').val(),
        auth: window.localStorage.getItem('sestee')
      };
      if (tee.address && tee.passwd && tee.auth) {
        $.ajax({
          method: 'POST',
          url: '/api/change-m',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#changepwd-submit', function() {
      $(this).blur();
      let tee = {
        passwd: $('#curpwd').val(),
        newpwd: $('#newpwd').val(),
        confirma: $('#newpwdconfirm').val(),
        auth: window.localStorage.getItem('sestee')
      };
      if (tee.passwd && tee.newpwd && tee.confirma && tee.auth) {
        $.ajax({
          method: 'POST',
          url: '/api/change-passwd',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('change', '#image', function() {
      let file = $(this)[0].files[0];
      if (file.size <= 204800) {
        let fd = new FormData($('#ava-form')[0]);
        fd.append('token', window.localStorage.getItem('sestee'));
        $.ajax({
          method: 'POST',
          url: '/api/change-ava',
          processData: false,
          contentType: false,
          cache: false,
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: fd,
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      } else {
        let d = {'message': 'Недопустимый размер файла.'};
        showError('#mc', d);
        scrollPanel($('#ealert'));
      }
    });
    $('body').on('click', '#description-submit', function() {
      $(this).blur();
      if (!$('#description-editor').parents('.form-group')
                                   .hasClass('has-error')) {
        $.ajax({
          method: 'PUT',
          url: '/api/profile',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            auth: window.localStorage.getItem('sestee'),
            text: $('#description-editor').val()
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
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
    $('body').on(
      'keyup', '#description-editor',
      {len: 500, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $('body').on('click', '#cancel-description', function() {
      $(this).blur();
      $(this).parents('#description-e').slideUp('slow');
      let description = $('#description-block');
      description.slideDown('slow', function() { scrollPanel(description); });
    });
    $('body').on('click', '#fix-description', function() {
      $(this).blur();
      let emf = $('#changeemf');
      if (!emf.is(':hidden')) emf.slideUp('slow');
      let pwdf = $('#changepwdf');
      if (!pwdf.is(':hidden')) pwdf.slideUp('slow');
      let avaf = $('#changeavaf');
      if (!avaf.is(':hidden')) avaf.slideUp('slow');
      $(this).parents('#description-block').slideUp('slow');
      let editor = $('#description-e');
      editor.slideDown('slow', function() { scrollPanel(editor); });
      $('#description-editor').focus();
    });
    $('body').on('click', '#emchange', function() {
      $(this).blur();
      let em = $('#changeemf');
      if (em.is(':hidden')) {
        $('#changeavaf').slideUp('slow');
        $('#changepwdf').slideUp('slow');
        let de = $('#description-e');
        if (!de.is(':hidden')) {
          de.slideUp('slow');
          $('#description-block').slideDown('slow');
        }
        em.slideDown('slow', function() {
          scrollPanel(em);
          checkPC(860);
        });
      } else {
        em.slideUp('slow', function() {
          checkPC(860);
        });
      }
    });
    $('body').on('click', '#changepwd', function() {
      $(this).blur();
      let pwd = $('#changepwdf');
      if (pwd.is(':hidden')) {
        $('#changeavaf').slideUp('slow');
        $('#changeemf').slideUp('slow');
        let de = $('#description-e');
        if (!de.is(':hidden')) {
          de.slideUp('slow');
          $('#description-block').slideDown('slow');
        }
        pwd.slideDown('slow', function() {
          scrollPanel(pwd);
          checkPC(860);
        });
      } else {
        pwd.slideUp('slow', function() {
          checkPC(860);
        });
      }
    });
    $('body').on('click', '#changeava', function() {
      $(this).blur();
      let ava = $('#changeavaf');
      if (ava.is(':hidden')) {
        $('#changepwdf').slideUp('slow');
        $('#changeemf').slideUp('slow');
        let de = $('#description-e');
        if (!de.is(':hidden')) {
          de.slideUp('slow');
          $('#description-block').slideDown('slow');
        }
        ava.slideDown('slow', function() {
          scrollPanel(ava);
          checkPC(860);
        });
      } else {
        ava.slideUp('slow', function() {
          checkPC(860);
        });
      }
    });
  }
  if (ses) checkIncomming(ses);
  checkPC(860);
});
