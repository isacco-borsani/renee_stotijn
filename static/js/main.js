$(document).ready(function () {
    $.ajax({
        url: '/get_paints',
    }).done(function (data) {
        console.log(data['content'].length);
        $('.tiles__line-img').each(function () {
            console.log('background-image', 'url(static/images/quadri/' + data['content'][Math.floor(Math.random() * data['content'].length)] + ')')
            $(this).css('background-image', 'url(static/images/quadri/' + data['content'][Math.floor(Math.random() * data['content'].length)] + ')')
        })
    });


})

$(window).on('scroll', function () {
    console.log('Event Fired');
});
