function checkPermissions(ses) {
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')} : {};
  $.ajax({
    method: 'GET',
    url: '/api/admin-aliases',
    headers: tee,
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#searcht').html(), data);
        $('#mc').append(html);
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
}
