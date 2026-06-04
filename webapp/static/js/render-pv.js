function renderPV(page) {
  $('.page-num').each(function() {
    let p = parseInt($(this).text().trim());
    if (p == 0) {
      $(this).text('...').addClass('page-empty');
    } else if (p == page) {
      $(this).addClass('page-current');
    } else {
      $(this).addClass('page-link');
    }
  });
}
