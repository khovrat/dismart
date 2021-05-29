$('.page-link-active').click(function (event) {
    event.preventDefault();
    var page = $(this).attr('href');
    $.ajax({
        type: "GET",
        url: $('#name-pagination').val(),
        data: {
            page: page,
            type: $('#type-refresh').val(),
            language: $('#language-refresh').val(),
            amount: $('#amount-refresh').val(),
            rating: $('#rating-refresh').val(),
            sort: $('#sort-refresh').val(),
            intensity: $('#intensity-refresh').val(),
            term: $('#term-refresh').val(),
            readiness: $('#readiness-refresh').val(),
            size: $('#size-refresh').val(),
            age_left: $('#age-left').val(),
            age_right: $('#age-right').val()
        },
        success: function (response) {
            $('#content-pagination').html(response);
        },
        error: function () {
        }
    });
});
