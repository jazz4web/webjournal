$(function() {
  "use strict";
  checkAuth(ses);
  renderMenu();
  renderFooter();
  $('body').on('click', '.closeable', closeTopFlashed);
  showDrafts('/api/drafts', page, ses);
  if (ses) {
    $('body').on('click', '#next-link', {page:page}, linkNext);
    $('body').on('click', '#prev-link', {page:page}, linkPrev);
    $('body').on('click', '.page-link', linkPage);
    $('body').on('click', '.alias-link', function(event) {
      $(this).blur();
    });
    $('body').on('click', '#title-submit', function() {
      let title = $('#title');
      title.blur();
      $(this).blur();
      if (!$('.input-field').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: '/api/drafts',
          headers: {
            'x-br-ses': ses,
            'x-br-tee': checkBR()
          },
          data: {
            auth: window.localStorage.getItem('sestee'),
            title: title.val().trim()
          },
          success: function(data) {
            if (data.draft) {
              window.location.assign(data.draft);
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
    $('body').on('keyup', '#title', function(event) {
      if (event.which === 13) {
        $('#title-submit').trigger('click');
      }
    });
    $('body').on(
      'keyup blur', '#title', {min:3,max:100,block:'.input-field'},
      markInputError);
  }
  checkPC(860);
});
