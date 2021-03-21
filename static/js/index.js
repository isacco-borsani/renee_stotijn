$(document).ready(function () {
    $.ajax({
        url: '/get_paints',
    }).done(function (data) {
        $('.tiles__line-img').each(function () {
            $(this).css('background-image', 'url(static/images/quadri/' + data['content'][Math.floor(Math.random() * data['content'].length)] + ')')
        })
    });


})