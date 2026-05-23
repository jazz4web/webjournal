$(function() {
  "use strict";
  renderMenu();
  renderFooter();
  getCaptcha('#rfpt');
  $('body').on('click', '#rfp-submit', {'url': '/api/rfp'}, regSubmit);
  $('body').on('click', '#lcaptcha-reload',
    {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
    captchaReload);
  $('body').on('click', '#rfp-reg', function() {
    $(this).blur();
    window.location.assign('/?realm=reg');
  });
  $('body').on('keyup', '#lcaptcha', function(event) {
    if (event.which === 13) {
      if ($('#raddress').val()) {
        if ($(this).val()) $('#rfp-submit').trigger('click');
      }
    }
  });
  setTimeout(setCookies, 900);
  checkPC(860);
});
