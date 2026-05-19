function checkBR() {
  let sample;
  // samples from custom.js
  for (const each of samples) {
    let s = window.localStorage.getItem(each);
    if (s) sample = s;
  }
  let br = sample + navigator.userAgent + navigator.language +
    new Date().getTimezoneOffset() +
    screen.colorDepth +
    window.localStorage.getItem('ses');
  return SparkMD5.hash(br);
}
