function renameAlbum(event) {
  $(this).blur();
  let suffix = event.data.suffix ? event.data.suffix : $(this).data().suffix;
  let cur = $('#old-title').attr('title').trim();
  let nt = $('#title-change').val().trim();
  if (!$('#rename-form').hasClass('has-error') && nt !== cur) {
    $.ajax({
      method: 'PUT',
      url: '/api/pictures/' + suffix,
      headers: {
        'x-br-ses': ses,
        'x-br-tee': checkBR()
      },
      data: {
        auth: window.localStorage.getItem('sestee'),
        field: 'title',
        value: nt
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
}
