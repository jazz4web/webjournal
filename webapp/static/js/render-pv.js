function linkPage(event) {
  window.location.assign(
    window.location.pathname + '?page=' + $(this).text().trim());
}

function linkNext(event) {
  let p = event.data.page + 1;
  window.location.assign(
    window.location.pathname + '?page=' + p);
}

function linkPrev(event) {
  let p = event.data.page -1;
  window.location.assign(
    window.location.pathname + '?page=' + p);
}

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
