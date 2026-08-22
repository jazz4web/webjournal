function showCommentaries(slug, ses) {
  let tee = ses ? {
    'x-auth-sestee': window.localStorage.getItem('sestee')
  } : {
    'x-auth-sestee': 'empty'
    };
  $.ajax({
    method: 'GET',
    url: '/api/comment',
    headers: tee,
    data: {
      slug: slug
    },
    success: function(data) {
      if (data.commentaries) {
        b = '<div id="entity-commentaries" class="hidden"></div>';
        $('#page-content').append(b);
        for (let each of data.commentaries) {
          let html = Mustache.render($('#brancht').html(), each);
          $('#entity-commentaries').append(html);
          showChildren(each.children, each.id);
        }
        $('.commentary-attributes .date-field').each(function() {
          formatDateTime($(this));
        });
        checkPC(860);
        $('.commentary-body iframe').each(adjustFrame);
        $('.commentary-body').children().each(setMargin);
        $('.commentary-body img').each(adjustImage);
        $('#entity-commentaries').slideDown('slow');
      }
    },
    error: error403,
    dataType: 'json'
  });
}
