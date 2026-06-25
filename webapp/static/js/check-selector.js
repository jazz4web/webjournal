function checkSelector(elem, value) {
  let s = $(elem);
  for (let n = 0; n < s.length; n++) {
    if (s[n].value == value) {
      $(s[n]).attr('selected', 'selected');
    }
  }
}
