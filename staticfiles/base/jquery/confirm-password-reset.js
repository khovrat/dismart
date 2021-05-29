$('#password, #confirm-password').on('keyup', function () {
    if ($('#password').val() === $('#confirm-password').val()) {
        $('#matching').css('display', 'initial');
        $('#not-matching').css('display', 'none');
    } else if ($('#confirm-password').val() === ""|| $('#confirm-password').val() === 0 || $('#confirm-password').val() === undefined) {
        $('#matching').css('display', 'none');
        $('#not-matching').css('display', 'none');
    } else {
        $('#matching').css('display', 'none');
        $('#not-matching').css('display', 'initial');
    }
    checkBlock();
});