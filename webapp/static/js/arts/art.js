$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  checkAuth(ses);
  $('body').on('click', '.closeable', closeTopFlashed);
  $('body').on('click', '.copy-link', showCopyForm);
  $('body').on('click', '.entity-text-block img', clickImage);
  $('body').on('click', '#move-screen-up', moveScreenUp);
  showArt('/api/art', slug, ses);
  pingUser(300000, 12);
  if (ses) {
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
