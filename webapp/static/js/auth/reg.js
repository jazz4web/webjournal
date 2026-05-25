$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  if (ses) {
    $('#mc').removeClass('nonlisted');
    checkAuth(ses);
    if ($('.today-field').length) {
      renderTF('.today-field', luxon.DateTime.now());
    }
  } else {
    sendAuth('/api/reg', key, '#regt');
    $('body').on('click', '#crp-submit', function() {
      $(this).blur();
      let tee = {
        username: $('#username').val(),
        passwd: $('#crpassword').val(),
        confirma: $('#confirmation').val(),
        key: key
      };
      if (tee.username && tee.passwd && tee.confirma) {
        $.ajax({
          method: 'PUT',
          url: '/api/reg',
          data: tee,
          success: function(data) {
            if (data.done) {
              window.location.replace('/');
            } else {
              showError('#mc', data);
              scrollPanel($('#ealert'));
            }
          },
          dataType: 'json'
        });
      }
    });
  }
  checkPC(860);
});
