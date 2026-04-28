function renderMenu() {
  $('body').on('mouseleave', '.open', function() {
    if ($('.navbar-toggle').is(':hidden')) {
      $('.open').slideUp('slow').removeClass('open');
    }
  });
  $('body').on('mouseleave', '.menu-box', function() {
    if (!$('.navbar-toggle').is(':hidden')) {
      $('.menu-box').slideUp('slow', function() {
        $('.menu-box').removeAttr('style');
        $('.open').slideUp().removeClass('open');
      });
    }
  });
  $('body').on('mouseenter', '.item-link', function() {
    $(this).parent().addClass('pointed');
  });
  $('body').on('mouseleave', '.item-link', function() {
    $(this).parent().removeClass('pointed');
  });
  $('body').on('click', '.menu-item-link', function(event) {
    event.preventDefault();
    event.stopPropagation();
    let ibox = $(this).siblings('.items-box');
    if (ibox.is(':hidden')) {
      $('.open').slideUp('slow').removeClass('open');
      ibox.addClass('open').slideDown('slow');
    } else {
      ibox.slideUp('slow', function() { ibox.removeClass('.open');});
    }
  });
  $('body').on('click', '.navbar-toggle', function() {
    let menu = $('.menu-box');
    if (menu.is(':hidden')) {
      menu.slideDown('slow');
    } else {
      menu.slideUp('slow', function() {menu.removeAttr('style');});
    }
  });
  $(window).on('resize', function() {
    $('.menu-box').removeAttr('style');
    $('.items-box').removeAttr('style');
  });
}
