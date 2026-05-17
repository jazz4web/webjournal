function setCookies() {
  if (!window.localStorage.getItem('cookies')) {
    let html = Mustache.render($('#cookiesalertt').html(), {});
    $('#mc').after(html);
  }
  $('.deny-button').on('click', function() {
    window.location.replace('https://ya.ru');
  });
  $('.ok-button').on('click', function() {
    window.localStorage.setItem('cookies', 1);
    $('#cookies-alert').fadeOut('slow', function() {
      $('#cookies-alert').remove();
    });
  });
}
