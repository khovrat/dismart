$('#credit-card').on('keyup', function () {
    $(this).val(function (index, value) {
        value = value.replace(/\W/gi, '').replace(/(.{4})/g, '$1 ');
        if (value.substr(value.length - 1) === ' ') {
            return value.substr(0, value.length - 1);
        }
        return value;
    });
});