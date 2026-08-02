function showLabeledDrafts(url, page, label, ses) {
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {
    'x-auth-sestee': 'empty'
  };
  $.ajax({
    method: 'GET',
    url: url,
    headers: tee,
    data: {
      page: page,
      label: label
    },
    success: function(data) {
      checkData(data);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#draftst').html(), data);
        $('#mc').append(html);
        if ($('.today-field').length) {
          renderTF('.today-field', luxon.DateTime.now());
        }
        $('.date-field').each(function() { formatDateTime($(this)); });
        $('.entity-block').each(checkNext);
        $('.labels').each(fixComma);
        if (data.pv) renderPV(data.pagination.page);
        checkPC(860);
      }
    },
    error: error403,
    dataType: 'json'
  });
}
