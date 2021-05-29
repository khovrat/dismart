$('#filter-link').click(function (event) {
    event.preventDefault();
    $('#cancel-filter-link').css('display', 'initial');
    $.ajax({
        headers: { "X-CSRFToken": $('#csrf-token').val() },
        type: "POST",
        url: $(this).attr('href'),
        data: {
            page: $('.current-page').val(),
            language: $('#form-language').val().toString(),
            type: $('#form-type').val().toString(),
            sort: $('#form-sort').val()
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
    $('#cancel-filter-link').css('display', 'none');
    $.ajax({
        type: "GET",
        url: $(this).attr('href'),
        data: {
            page: $('.current-page').val(),
            sort: $('#form-sort').val()
        },
        success: function (response) {
            $('#content-pagination').html(response);
        },
        error: function () {
        }
    });
});
