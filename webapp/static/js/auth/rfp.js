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
    sendAuth('/api/rfp', key, '#rfpt');
    $('body').on('click', '#rsp-submit', function() {
      $(this).blur();
      let tee = {
        address: $('#rsaddress').val(),
        passwd: $('#rspassword').val(),
        confirma: $('#rsconfirm').val(),
        key: key
      };
      if (tee.address && tee.passwd && tee.confirma) {
        $.ajax({
          method: 'PUT',
          url: '/api/rfp',
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
