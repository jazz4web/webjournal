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
      console.log(data)
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#mc').append(html);
        checkPC(860);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        if ($('#select-group').length) {
          let s = $('#select-group option');
          for (let n = 0; n < s.length; n++) {
            if (s[n].value == data.user.group) {
              $(s[n]).attr('selected', 'selected');
            }
          }
        }
      }
    },
    dataType: 'json'
  });
  if (cu === username ) {
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
  checkPC(860);
});
