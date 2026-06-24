function showAlbumStat(elem, ses) {
  elem.addClass('clicked-item');
  let tee = ses ? {
    'x-br-ses': ses,
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {};
  $.ajax({
    method: 'GET',
    url: '/api/albumstat',
    headers: tee,
    data: {
      suffix: elem.data().suffix
    },
    success: function(data) {
      if (data.album) {
        let sb = $('.stat-block');
        if (sb.length) {
          $('.item-date-field').removeClass('item-date-field');
          sb.slideUp('slow', function() {
            sb.remove();
          });
        }
        let html = Mustache.render($('#astatt').html(), data);
        elem.after(html);
        $('.stat-block').slideDown('slow', function() { checkPC(860);});
        formatDateTime($('.item-date-field'));
        checkSelector(data.album.state);
        scrollPanel(elem);
      } else {
        showError('#mc', data);
        scrollPanel($('#ealert'));
        setTimeout(function() { checkPC(860); }, 400);
      }
    },
    dataType: 'json'
  });
}
