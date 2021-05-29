$(function () {
    $(document).scroll(function () {
        var $nav = $(".navbar-fixed-top");
        var $logo = $("#logo");
        $nav.toggleClass("scrolled", $(this).scrollTop() > $nav.height());
        if ($(this).scrollTop() > $nav.height())
            $logo.attr("src", $logo.attr("data-dark"));
        else
            $logo.attr("src", $logo.attr("data-white"));
    });
});