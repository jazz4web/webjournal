function hideButton() {
    $(this).blur();
    $('.remove-button').fadeOut('slow');
    let rb = $(this).siblings('.remove-button');
    if (rb.is(':hidden')) {
      rb.attr('style', 'display: inline-block');
    } else {
      rb.fadeOut('slow');
    }
}
