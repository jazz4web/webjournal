function logout(url, ses) {
  $.ajax({
    method: 'DELETE',
    url: url,
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      'token': window.localStorage.getItem('sestee')
    },
    success: function(data) {
      if (data.result) {
        window.localStorage.removeItem('sestee');
        window.location.assign('/');
      }
    },
    dataType: 'json'
  });
}
