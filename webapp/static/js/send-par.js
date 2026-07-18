function sendPar(slug, val, code) {
  $.ajax({
    method: 'POST',
    url: '/api/send-par',
    headers: {
      'x-br-ses': ses,
      'x-br-tee': checkBR()
    },
    data: {
      auth: window.localStorage.getItem('sestee'),
      slug: slug,
      text: val,
      code: code
    },
    success: function(data) {
      if (data.done) {
        if (!$('.entity-text-block').length) window.location.reload();
        if (data.html) {
          $('.entity-text-block')
            .empty().append(data.html).data('len', data.length);
          parseDraft();
        }
        $('#html-text-edit').val('');
        checkPC(860);
      } else {
        showError('#editor-block', data);
        $('#ealert').addClass('next-block');
        setTimeout(function() {
          checkPC(860);
        }, 400);
      }
    },
    dataType: 'json'
  });
}
