$('#sort-link').click(function (event) {
    event.preventDefault();
    $.ajax({
        type: "GET",
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
