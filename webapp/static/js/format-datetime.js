function formatDateTime(elem) {
  let dt = elem.text().trim();
  let d = luxon.DateTime.fromISO(dt)
                        .setLocale('ru')
                        .toLocaleString(luxon.DateTime.DATE_FULL);
  let t = luxon.DateTime.fromISO(dt).setLocale('ru').toFormat('T');
  elem.text(d + ', ' + t);
}
