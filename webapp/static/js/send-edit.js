function sendEdit(slug, num, insert, text, code) {
  $.ajax({
    method: 'PUT',
    url: '/api/send-par',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      slug: slug,
      num: num,
      insert: insert,
      text: text,
      code: code
    },
    success: function(data) {
      if (data.done) {
        if (data.html) {
          $('.entity-text-block')
            .empty().append(data.html).data('len', data.length);
          parseDraft();
          $('#editor-block').slideDown('slow');
        }
      } else {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
