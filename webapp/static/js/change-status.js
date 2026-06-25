function changeStatus(event) {
  let suffix = event.data.suffix ? event.data.suffix : $(this).data().suffix;
  $.ajax({
    method: 'PUT',
    url: '/api/pictures/' + suffix,
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      field: 'state',
      value: $(this).val()
    },
    success: function(data) {
      if (data.album) {
        window.location.replace('/pictures/' + suffix);
      } else {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
