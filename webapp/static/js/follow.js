function follow(event) {
  $(this).blur();
  $.ajax({
    method: 'PUT',
    url: '/api/follow',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      slug: event.data.slug
    },
    success: function(data) {
      if (data.message) {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() { checkPC(860); }, 400);
      } else {
        window.location.reload();
      }
    },
    dataType: 'json'
  });
}
