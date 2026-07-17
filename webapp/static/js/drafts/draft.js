$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showDraft(slug);
  if (ses) {
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
