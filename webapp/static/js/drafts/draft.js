$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showDraft(slug);
  if (ses) {
    checkIncomming(ses);
    $('body').on('change', '#select-status', {slug: slug}, function(event) {
      let state = $('#select-status').val();
      $.ajax({
        method: 'POST',
        url: '/api/draft',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          value: state,
          slug: event.data.slug
        },
        success: function(data) {
          if (data.done) {
            window.location.reload();
          } else {
            showError('#editor-block', data);
            $('#ealert').addClass('next-block');
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#special-case', {slug:slug}, function(event) {
      $(this).blur();
      undressLinks(event.data.slug);
    });
    $('body').on('click', '.edit-par', {slug: slug}, function(event) {
      $(this).blur();
      let par = $(this).parent().next();
      let num = $(this).data().num;
      let tee = ses ? {
        'x-br-ses': ses,
        'x-auth-sestee': window.localStorage.getItem('sestee')
      } : {};
      $.ajax({
        method: 'GET',
        url: '/api/send-par',
        headers: tee,
        data: {
          slug: event.data.slug,
          num: num
        },
        success: function(data) {
          if (data.text) {
            let d = {num: num, insert: 0, text: data.text};
            let html = Mustache.render($('#peditort').html(), d);
            par.after(html).slideUp('slow');
            $('#editor-opts').slideUp('slow');
            $('#paragraph-editor').slideDown('slow').css({'margin': 0});
            $('#editor-block').slideUp('slow');
          } else {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body')
      .on('keyup', '#paragraph-text-edit', {slug:slug}, function(event) {
        if (event.which == 13) {
          let val = $(this).val().trim();
          let insert = $(this).data().insert;
          let num = $(this).data().num;
          const F = '```';
          if (val.startsWith(F)) {
            if (val.indexOf(F, 1) >= 4 && val.endsWith(F)) {
              sendEdit(event.data.slug, num, insert, val, 1);
            }
          } else {
            sendEdit(event.data.slug, num, insert, val.replace('\n', ''), 0);
          }
        }
      });
    $('body').on('click', '#cancel-edit', function() {
      $(this).blur();
      if (!$('#paragraph-text-edit').data().insert) {
        $('#paragraph-editor').prev().slideDown('slow');
      }
      $('#paragraph-editor').slideUp('slow', function() {
        $(this).remove();
      });
      $('#editor-block').slideDown('slow');
    });
    $('body').on('click', '.add-before', {slug: slug}, function(event) {
      $(this).blur();
      let par = $(this).parent();
      let num = $(this).data().num;
      let html = Mustache.render($('#peditort').html(), {num:num, insert:1});
      par.before(html).fadeOut('slow');
      $('#paragraph-editor').slideDown('slow').css({'margin': 0});
      $('#paragraph-text-edit').focus();
      $('#editor-block').slideUp('slow');
    });
    $('body').on('click', '.remove-button', {slug: slug}, function(event) {
      $(this).blur();
      let num = $(this).data().num;
      $.ajax({
        method: 'DELETE',
        url: '/api/send-par',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          slug: event.data.slug,
          num: num
        },
        success: function(data) {
          if (data.done) {
            if (data.html) {
              $('.entity-text-block').empty()
                .append(data.html).data('len', data.length);
              parseDraft();
              $('#html-text-edit').val('');
            } else {
              window.location.reload();
            }
          } else {
            showError('#mc', data);
            $('#editor-opts').remove();
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('mouseleave', '.entity-text-block', function() {
      if (!$('#paragraph-editor').length) {
        $('#editor-opts').remove();
      }
    });
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('mouseenter', '.editable', function() {
      if(!$('#paragraph-editor').length && !$('#p-block').length) {
        $('#editor-opts').remove();
        let th = $(this);
        let d = {num: th.data().num};
        let html = Mustache.render($('#eoptst').html(), d);
        if (th[0].nodeName === 'LI') {
          if (th.find('p').length) {
            th.find('p').before(html);
          } else {
            th.before(html);
          }
        } else {
          th.before(html);
        }
      }
    });
    $('body').on('click', '.entity-text-block img', clickImage);
    $('body').on('keyup', '#html-text-edit', {slug: slug}, function(event) {
      let val = $(this).val().trim();
      if (event.which == 13) {
        const F = '```';
        if (val.startsWith(F)) {
          if (val.indexOf(F, 1) >= 4 && val.endsWith(F)) {
            sendPar(event.data.slug, val, 1);
          }
        } else if (val) {
          sendPar(event.data.slug, val.replace('\n', ''), 0);
        }
      }
    });
    $('body').on('click', '#summary-from-text', function() {
      $(this).blur();
      let l = $('.entity-text-block').children('p');
      let w = '';
      for (let n = 0; n < l.length && w.length < 512; n++) {
        w = w + ' ' + $(l[n]).text();
      }
      let t = w.trim().split(' ');
      let res = '';
      let i = 0;
      while ((res + '...').length <= 384 && i < t.length) {
        res = res + ' ' + t[i];
        i++;
      }
      $('#summary-edit').val(res.trim() + '...').trigger('blur');
    });
    $('body').on('click', '#summary-submit', {slug: slug}, function(event) {
      $(this).blur();
      if (!$('#summary-edit').parents('.form-group').hasClass('has-error')) {
        changeDraft('summary', $('#summary-edit').val(), event.data.slug);
      }
    });
    $('body').on(
      'keyup blur', '#summary-edit',
      {len: 512, marker: '#s-length-value', block: '#s-length-marker'},
      trackMarker);
    $('body').on('click', '#comments-state', {slug:slug}, function(event) {
      $(this).blur();
      changeDraft('commented', 'empty', event.data.slug);
    });
    $('body').on(
      'keyup blur', '#title',
      {min:3, max: 100, block: '.input-field'}, markInputError);
    $('body').on('click', '#title-submit', {slug: slug}, function(event) {
      $(this).blur();
      let prev = $(this).data().prev;
      let cur = $('#title').val().trim();
      if (!$('.input-field').hasClass('has-error') && cur !== prev) {
        changeDraft('title', $('#title').val(), event.data.slug);
      }
    });
    $('body').on(
      'keyup blur', '#metadesc-edit',
      {len:180,marker:'#d-length-value',block:'#d-length-marker'},
      trackMarker);
    $('body').on('click', '#metadesc-submit', {slug:slug}, function(event) {
      $(this).blur();
      if (!$('#metadesc-edit').parents('.form-group').hasClass('has-error')) {
        changeDraft('meta', $('#metadesc-edit').val(), event.data.slug);
      }
    });
    $('body').on('click', '#labels-submit', {slug:slug}, function(event) {
      $(this).blur();
      let e = $('#labels-edit').parents('.form-group-a');
      if (!e.hasClass('has-error')) {
        $.ajax({
          method: 'PUT',
          url: '/api/labels',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            auth: window.localStorage.getItem('sestee'),
            labels: $('#labels-edit').val().trim(),
            slug: event.data.slug
          },
          success: function(data) {
            if (data.labels) {
              window.location.reload();
            } else {
              showError('#editor-block', data);
              $('#ealert').addClass('next-block');
              setTimeout(function() { checkPC(860); }, 400);
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('keyup blur', '#labels-edit', function() {
      let g = $(this).parents('.form-group-a');
      g.removeClass('has-error');
      let c = $(this).val().split(',');
      for (let each in c) {
        each = c[each].trim();
        if (each) {
          let re = /^[A-Za-zА-Яа-яЁё\d\-]{1,32}$/;
          if (!re.exec(each)) {
            g.addClass('has-error');
          }
        }
      }
    });
    $('body').on('click', '#labels-button', function() {
      $(this).blur();
      changeForm('#labels-editor', '#labels-edit');
    });
    $('body').on('click', '#edit-metadesc', function() {
      $(this).blur();
      changeForm('#meta-description-editor', '#metadesc-edit');
    });
    $('body').on('click', '#edit-title', function() {
      $(this).blur();
      changeForm('#entity-title-editor', '#title');
    });
    $('body').on('click', '#edit-summary', function() {
      $(this).blur();
      changeForm('#summary-editor', '#summary-edit');
    });
    $('body').on('click', '#state-button', function() {
      $(this).blur();
      changeForm('#status-editor', '#select-status');
    });
    $('body').on('click', '#move-screen-up', moveScreenUp);
    $('body').on('click', '.copy-link', showCopyForm);
  }
  checkPC(860);
});
