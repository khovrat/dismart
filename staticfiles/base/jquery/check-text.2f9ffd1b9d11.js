$(document).ready(function () {
    $(".textInfo").keypress(function (event) {
        var inputValue = event.charCode;
        if (!(inputValue >= 65 && inputValue <= 120) && (inputValue !== 32 && inputValue !== 0)) {
            event.preventDefault();
        }
    });
});


$(document).ready(function () {
    var chars = '';
    $("#revenueInfo").keypress(function (event) {
        chars = String.fromCharCode(event.keyCode).toLowerCase();
        if (!chars.match(/^[-\d\,\.]$/)) {
            event.preventDefault();
        } else if ((chars === ',' || chars === '.' || chars === '-') && $("#revenueInfo").val().includes(chars)) {
            event.preventDefault();
        }
    });
});


$(document).ready(function () {
    var chars = '';
    $("#termInfo").keypress(function (event) {
        chars = String.fromCharCode(event.keyCode).toLowerCase();
        if (!chars.match(/^[\d\,\.]$/)) {
            event.preventDefault();
        } else if ((chars === ',' || chars === '.') && $("#termInfo").val().includes(chars)) {
            event.preventDefault();
        }
    });
});

$(document).ready(function () {
    var chars = '';
    $("#age-left").keypress(function (event) {
        chars = String.fromCharCode(event.keyCode).toLowerCase();
        if (!chars.match(/^[\d]$/)) {
            event.preventDefault();
        }
    });
    $("#age-right").keypress(function (event) {
        chars = String.fromCharCode(event.keyCode).toLowerCase();
        if (!chars.match(/^[\d]$/)) {
            event.preventDefault();
        }
    });
    $("#size").keypress(function (event) {
        chars = String.fromCharCode(event.keyCode).toLowerCase();
        if (!chars.match(/^[\d]$/)) {
            event.preventDefault();
        }
    });
});
