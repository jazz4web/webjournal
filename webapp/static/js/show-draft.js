function showDraft(slug) {
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {};
  $.ajax({
    method: 'GET',
    url: '/api/draft',
    headers: tee,
    data: {
      slug: slug
    },
    success: function(data) {
      console.log(data);
      if (data.draft) {
        $('title').text($('title').text().trim() + ' ' + data.draft.title);
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftt').html(), data);
        $('#mc').append(html);
        let ed = Mustache.render($('#editort').html(), data);
        $('#mc').after(ed);
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('#copy-button').on('click', {cls:'#link-copy-form'}, copyThis);
        checkSelector('#select-status option', data.draft.state);
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
}
