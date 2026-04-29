function resize(wwidth, width) {
  if (wwidth > width) {
    $('#page-content').css({"width": width - 20});
  } else {
    $('#page-content').css({"width": wwidth - 20});
  }
}

function checkPC(width) {
  let wwidth = $(window).width();
  let mcon = $('#page-content');
  resize(wwidth, width);
  $(window).on('resize', function() {
    let wwidth = $(window).width();
    resize(wwidth, width);
  });
}

