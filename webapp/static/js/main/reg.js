$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  if (c) {
    getCaptcha('#regt');
    $('body').on('click', '#lcaptcha-reload',
      {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
      captchaReload);
    $('body').on('keyup', '#lcaptcha', function(event) {
      if (event.which === 13) {
        if ($('#raddress').val()) {
          if ($(this).val()) $('#reg-submit').trigger('click');
        }
      }
    });
    $('body').on('click', '#reg-submit', {'url': '/api/reg'}, regSubmit);
  } else {
    let form = Mustache.render($('#regt').html(), {});
    $('#mc').append(form);
    if ($('.today-field').length) {
      renderTF('.today-field', luxon.DateTime.now());
    }
  }
  setTimeout(setCookies, 900);
  checkPC(860);
});
