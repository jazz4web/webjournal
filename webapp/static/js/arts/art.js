$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  checkAuth(ses);
  $('body').on('click', '.closeable', closeTopFlashed);
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '.slidable', hideAnnounce);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  showArt('/api/art', slug, ses);
  pingUser(300000, 12);
  showCommentaries(slug, ses);
  $('body').on('click', '#cancel-answer', function() {
    $(this).blur();
    let nab = $('.new-answer-block');
    nab.slideUp('slow', function() {
      nab.remove();
    });
  });
  $('body').on('click', '.answer-button', function() {
    $(this).blur();
    let ncb = $('.new-comment-block');
    if (ncb.length) ncb.slideUp('slow', function() {ncb.remove();});
    let par = $(this).parents('.root-commentary');
    let cid = $(this).data().id;
    $.ajax({
      method: 'POST',
      url: '/api/answer',
      headers: {
        'x-br-ses': ses,
        'x-br-tee': checkBR()
      },
      data: {
        auth: window.localStorage.getItem('sestee'),
        cid: cid
      },
      success: function(data) {
        let html = Mustache.render($('#sanswert').html(), data);
        let al = $('.comment-alert');
        if (al.length) al.remove();
        let nab = $('.new-answer-block');
        if (nab.length) nab.slideUp('slow', function() {nab.remove();});
        par.after(html);
        if (data.perm) {
          $('.new-answer-block').slideDown('slow', function() {
            scrollPanel($('.new-answer-block'));
          });
        } else {
          $('.comment-alert').slideDown('slow');
        }
      },
      dataType: 'json'
    });
  });
  $('body').on('click', '#new-comment-add', function() {
    $(this).blur();
    let nab = $('.new-answer-block');
    if (nab.length) nab.slideUp('slow', function() {nab.remove(); });
    let form = $('.new-comment-block');
    if (form.length) {
      if (form.is(':hidden')) {
        form.slideDown('slow', function() {
          scrollPanel($('.comments-options'));
        });
      } else {
        form.slideUp('slow');
      }
    } else {
      $.ajax({
        method: 'POST',
        url: '/api/art',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          slug: slug
        },
        success: function(data) {
          let html = Mustache.render($('#scommentt').html(), data);
          let al = $('.comment-alert');
          if (al.length) al.remove();
          let ncb = $('.new-comment-block');
          if (ncb.length) ncb.remove();
          $('#mc').after(html);
          if (data.perm) {
            $('.new-comment-block').slideDown('slow', function() {
              scrollPanel($('.comments-options'));
            });
          } else {
            $('.comment-alert').slideDown('slow');
          }
        },
        dataType: 'json'
      });
    }
  });
  if (ses) {
    $('body').on('click', '.trash-button', hideButton);
    $('body').on('click', '.remove-commentary', function() {
      $(this).blur();
      let par = $(this).parents('.root-commentary');
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
            window.location.reload();
          } else {
            showError(par, data);
            $('#ealert').addClass('next-block');
            scrollPanel($('#ealert'));
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#answer-submit', function() {
      $(this).blur();
      let pid = $(this).data().pid;
      let text = $('#answer-editor').val();
      if (text) {
        $.ajax({
          method: 'PUT',
          url: '/api/answer',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            slug: slug,
            pid: pid,
            auth: window.localStorage.getItem('sestee'),
            text: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('.new-answer-block', data);
              $('#ealert').addClass('next-block');
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    $('body').on('click', '#comment-submit', function() {
      $(this).blur();
      let text = $('#comment-editor').val();
      if (text) {
        $.ajax({
          method: 'POST',
          url: '/api/comment',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            slug: slug,
            auth: window.localStorage.getItem('sestee'),
            text: text
          },
          success: function(data) {
            if (data.done) {
              window.location.reload();
            } else {
              showError('.new-comment-block', data);
              $('#ealert').addClass('next-block');
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
    checkIncomming(ses);
    $('body').on('click', '#censor-this', {slug: slug}, censorThis);
    $('body').on('click', '#special-case', {slug: slug}, function(event) {
      $(this).blur();
      undressLinks(event.data.slug);
    });
    $('body').on('click', '#tape-out', {slug: slug}, follow);
    $('body').on('click', '#tape-in', {slug: slug}, follow);
    $('body').on('click', '#dislike-button', {slug:slug}, function(event) {
      $(this).blur();
      $.ajax({
        method: 'PUT',
        url: '/api/dislike',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          } else {
            if (data.done) {
              $('.like-block .value').text(data.likes);
              $('.dislike-block .value').text(data.dislikes);
              $('#like-button .value').text(data.likes);
              $('#dislike-button .value').text(data.dislikes);
              if (data.liked) {
                $('#like-button').removeClass('btn-danger')
                                 .addClass('btn-success')
                                 .attr('title', 'нравится');

              }
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#like-button', {slug:slug}, function(event) {
      $(this).blur()
      $.ajax({
        method: 'PUT',
        url: '/api/like',
        headers: {
          'x-br-ses': ses,
          'x-br-tee': checkBR()
        },
        data: {
          auth: window.localStorage.getItem('sestee'),
          slug: event.data.slug
        },
        success: function(data) {
          if (data.message) {
            showError('#mc', data);
            scrollPanel($('#ealert'));
            setTimeout(function() { checkPC(860); }, 400);
          } else {
            $('.like-block .value').text(data.likes);
            $('.dislike-block .value').text(data.dislikes);
            $('#like-button .value').text(data.likes);
            $('#dislike-button .value').text(data.dislikes);
            if (data.liked) {
              $('#like-button').removeClass('btn-danger')
                               .addClass('btn-success')
                               .attr('title', 'нравится');
            } else {
              $('#like-button').removeClass('btn-success')
                               .addClass('btn-danger')
                               .attr('title', 'уже нравится');
            }
          }
        },
        dataType: 'json'
      });
    });
    $('body').on('click', '#editor-button', function() {
      $(this).blur();
      window.location.assign($(this).data().link);
    });
  }
  checkPC(860);
  setTimeout(setCookies, 900);
});
