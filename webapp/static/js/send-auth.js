function sendAuth(url, key, tid) {
  $.ajax({
    method: 'GET',
    url: url,
    headers: {
      'x-rfp-token': key
    },
    success: function(data) {
      if (data.aid) {
        let html = Mustache.render($(tid).html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          let dt = luxon.DateTime.now();
          renderTF('.today-field', dt);
        }
        checkPC(860);
      } else {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html).removeClass('nonlisted');
        slidePage('#ealert');
      }
    },
    dataType: 'json'
  });
}
