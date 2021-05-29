$('#filter-link').click(function (event) {
    event.preventDefault();
    $('#filter-link').css('display', 'none');
    $('#cancel-filter-link').css('display', 'initial');
    $.ajax({
        type: "GET",
        url: $(this).attr('href'),
        data: {
            page: $('.current-page').val()
        },
        success: function (response) {
            $('#content-pagination').html(response);
        },
        error: function () {
        }
    });
});

$('#cancel-filter-link').click(function (event) {
    event.preventDefault();
    $('#filter-link').css('display', 'initial');
    $('#cancel-filter-link').css('display', 'none');
    $.ajax({
        type: "GET",
        url: $(this).attr('href'),
        data: {
            page: $('.current-page').val()
        },
        success: function (response) {
            $('#content-pagination').html(response);
        },
        error: function () {
        }
    });
});
