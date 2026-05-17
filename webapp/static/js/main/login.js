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
  setTimeout(setCookies, 900);
});
