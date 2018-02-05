// mostly based on https://gist.github.com/csasbach/867744
function helpwidget_onload(elem) {
    $(elem).data('title', $(elem).attr('title'));
    $(elem).removeAttr('title');
}

function helpwidget_onmouseover(elem) {
    // first remove all existing abbreviation tooltips
    $('.tooltip').remove();
    // create the tooltip
    $('body').append('<span class="tooltip">' + $(elem).data('title') + '</span>');
    // position the tooltip 4 pixels above and 4 pixels to the left of the abbreviation
    let left = $(elem).offset().left + $(elem).width() + 4;
    let top = $(elem).offset().top - 4;
    $('.tooltip').css('left', left);
    $('.tooltip').css('top', top);
}

function helpwidget_onclick(elem) {
    $(elem).mouseover();
    // after a slight 2 second fade, fade out the tooltip for 1 second
    $('.tooltip').animate({opacity: 0.9}, {
        duration: 2000, complete: function () {
            $(this).fadeOut(1000);
        }
    });
}

function helpwidget_onmouseout(elem) {
    $('.tooltip').remove();
}
