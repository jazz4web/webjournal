function changeDraft(field, value, slug) {
  $.ajax({
    method: 'PUT',
    url: '/api/draft',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      field: field,
      value: value,
      slug: slug
    },
    success: function(data) {
      if (data.done) {
        if (data.slug) {
          window.location.replace('/drafts/' + data.slug);
        } else {
          window.location.reload();
        }
      } else {
        showError('#editor-block', data);
        $('#ealert').addClass('next-block');
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
