function showArt(url, slug, ses) {
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
      slug: slug
    },
    success: function(data) {
      checkData(data);
      if (data.art) {
        $('title').text($('title').text().trim() + ' ' + data.art.title);
      } else {
        $('title').text($('title').text().trim() + ' доступ закрыт');
      }
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#mc').removeClass('nonlisted').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#artt').html(), data);
        $('#mc').append(html);
        if (!data.own && !data.admin) countClicks(data.art.suffix);
        $('.entity-attributes .date-field').each(function() {
          formatDateTime($(this));
        });
        $('#copy-button').on('click', {cls: '#link-copy-form'}, copyThis);
        $('.labels').each(fixComma);
        checkPC(860);
        $('.entity-text-block iframe').each(adjustFrame);
        $('.entity-text-block').children().each(setMargin);
        $('.entity-text-block img').each(adjustImage);
      }
    },
    dataType: 'json'
  });
}
