function ping() {
  $.ajax({
    method: 'POST',
    url: '/api/index',
    data: {
      auth: window.localStorage.getItem('sestee')
    },
    success: function(data) {
      if (data.redirect) window.location.reload();
    },
    dataType: 'json'
  });
}
