function checkIncomming(ses) {
  $.ajax({
    method: 'GET',
    url: '/api/convs',
    headers: {
      'x-br-ses': ses,
      'x-auth-sestee': window.localStorage.getItem('sestee')
    },
    data: {
      justcount: 1
    },
    success: function(data) {
      if (data.pm) {
        let interval = setInterval(function() {
          if ($('#mc').length) {
            let flashed = $('.top-flashed-block');
            d = {'flashed': flashed.length,
                 'pm': data.pm};
            let html = Mustache.render($('#pmalertt').html(), d);
            if (flashed.length) {
              flashed.append(html);
            } else {
              $('#mc').before(html);
            }
            clearInterval(interval);
          }
        }, 10);
      }
    },
    dataType: 'json'
  });
}
