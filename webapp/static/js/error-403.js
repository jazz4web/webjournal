function error403(data) {
  if (data.status == 403) {
    let html = Mustache.render(
      $('#ealertt').html(), {'message': 'Доступ ограничен.'});
    $('#mc').append(html);
    slidePage('#ealert');
  }
}
