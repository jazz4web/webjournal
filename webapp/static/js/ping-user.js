function pingUser(timeout, length) {
  let now = luxon.DateTime.now();
  let interval = setInterval(function() {
    ping();
    let cur = luxon.DateTime.now();
    if (cur > now.plus({hours: length})) {
      clearInterval(interval);
    }
  }, timeout, now);
}
