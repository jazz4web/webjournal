function renderFooter() {
  let dt = luxon.DateTime.now();
  let sdate = $('#footer-link').data().date;
  let sname = $('#footer-link').data().name;
  if (sdate < dt.c.year) {
    sdate = sdate + "&ndash;" + dt.c.year;
    $('#footer-link').html("&copy; " + sname + ", " + sdate + " гг.");
  }
}
