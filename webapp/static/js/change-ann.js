function changeAnn(field, value, suffix) {
  $.ajax({
    method: 'PUT',
    url: '/api/announce',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      field: field,
      value: value,
      suffix: suffix,
      auth: window.localStorage.getItem('sestee')
    },
    success: function(data) {
      if (data.done) {
        window.location.reload();
      } else {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() {checkPC(860);}, 400);
      }
    },
    dataType: 'json'
  });
}
