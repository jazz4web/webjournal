$(function() {
  "use strict";
  //samples from custom.js, item and value from login.html
  for (const each of samples) {
    if (each != item) {
      window.localStorage.removeItem(each);
    } else {
      window.localStorage.setItem(item, value);
    }
  }
  renderMenu();
  renderFooter();
  getCaptcha('#logint');
  $('body').on('click', '#lcaptcha-reload',
    {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
    captchaReload);
  $('body').on('click', '#login-submit', function() {
    $(this).blur();
    let tee = {
      login: $('#logininput').val(),
      passwd: $('#password').val(),
      rme: $('#remember_me').is(':checked') ? 1 : 0,
      cache: $('#lsuffix').val(),
      captcha: $('#lcaptcha').val()
    };
    if (tee.login && tee.passwd && tee.captcha && tee.cache) {
      $.ajax({
        method: 'POST',
        url: '/api/login',
        headers: {
          'x-br-tee': checkBR()
        },
        data: tee,
        success: function(data) {
          if (data.token) {
            window.localStorage.setItem('sestee', data.token);
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
  $('body').on('click', '#login-reg', function() {
    $(this).blur();
    window.location.assign('/?realm=rfp');
  });
  $('body').on('keyup', '#lcaptcha', function(event) {
    if (event.which === 13) {
      if ($('#logininput').val() && $('#password').val()) {
        if ($(this).val()) $('#login-submit').trigger('click');
      }
    }
  });
  setTimeout(setCookies, 900);
  checkPC(860);
});
