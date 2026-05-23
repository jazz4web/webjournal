function regSubmit(event) {
  $(this).blur();
  let tee = {
    address: $('#raddress').val(),
    cache: $('#lsuffix').val(),
    captcha: $('#lcaptcha').val()
  };
  if (tee.address && tee.cache && tee.captcha) {
    $.ajax({
      method: 'POST',
      url: event.data.url,
      data: tee,
      success: function(data) {
        if (data.done) {
          window.location.replace('/');
        } else {
          showError('#mc', data);
          scrollPanel($('#ealert'));
        }
      },
      dataType: 'json'
    });
  }
}
