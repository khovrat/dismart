$('#ex-month, #ex-year').on('keyup', function () {
    if ($('#ex-month').val() === "" || $('#ex-year').val() === "") {
        $('#confirm').css('display', 'none');
        $('#not-confirm').css('display', 'none');
    } else {
        var today = new Date();
        var someday = new Date();
        someday.setFullYear(parseInt($('#ex-year').val()), $('#ex-month').val(), 1);
        if (someday < today) {
            $('#confirm').css('display', 'none');
            $('#not-confirm').css('display', 'initial');
            $('#payment-btn').prop('disabled', true);
        } else {
            $('#confirm').css('display', 'initial');
            $('#not-confirm').css('display', 'none');
            $('#payment-btn').prop('disabled', false);
        }
    }

});