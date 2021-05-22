$(document).ready(function () {
    $.ajax({
        url: '/get_paints',
    }).done(function (data) {
        $('.tiles__line-img').each(function () {
            let index = Math.floor(Math.random() * data['content'].length);
            $(this).attr('data-paint-location', '/static/images/quadri/web/' + data['content'][index]);
            $(this).css('background-image', 'url(static/images/quadri/web/' + data['content'][index] + ')')
        })
    });


})