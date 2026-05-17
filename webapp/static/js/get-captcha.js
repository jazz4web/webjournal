function getCaptcha(eid) {
  $.ajax({
    method: 'GET',
    url: '/api/captcha',
    success: function(data) {
      let dt = luxon.DateTime.now();
      let form = Mustache.render($(eid).html(), data);
      $('#mc').append(form);
      if ($('.today-field').length) renderTF('.today-field', dt);
      if (eid === '#logint') window.localStorage.setItem(
        'ses', $('#lsuffix').val().split(':')[1]);
      checkPC(860);
    },
    dataType: 'json'
  });
}
