function renderLastSeen(elem) {
  let text = elem.text().trim();
  elem.text(luxon.DateTime.fromISO(text).setLocale('ru').toRelative());
}
