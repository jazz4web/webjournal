function undressLinks(slug) {
  $.ajax({
    method: 'PATCH',
    url: '/api/draft',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      slug: slug
    },
    success: function(data) {
      if (data.done) {
        window.location.reload();
      } else {
        if ($('#editor-block').length) {
          showError('#editor-block', data);
          $('#ealert').addClass('next-block');
        } else {
          showError('#mc', data);
          scrollPanel($('#ealert'));
        }
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
