function remPic(event) {
  $(this).blur();
  let p = ($('.remove-button').length > 1) ?
    event.data.page : event.data.page -1;
  let suffix = $(this).data().suffix;
  $.ajax({
    method: 'DELETE',
    url: '/api/admin-pictures',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      suffix: suffix,
      page: p,
      auth: window.localStorage.getItem('sestee'),
      endpoint: window.location.pathname
    },
    success: function(data) {
      if (data.done) {
        window.location.replace(data.url);
      } else {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
