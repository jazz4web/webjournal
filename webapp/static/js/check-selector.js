function checkSelector(state) {
  let s = $('#select-status option');
  for (let n = 0; n < s.length; n++) {
    if (s[n].value == state) {
      $(s[n]).attr('selected', 'selected');
    }
  }
}
