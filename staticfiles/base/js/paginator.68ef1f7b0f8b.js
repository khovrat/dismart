class Index {

    static initPaginator() {
        document.body.querySelectorAll('.pagination > li > a')
            .forEach(link => link.addEventListener('click', Index.pagination_link_clickHandler));
    }

    static pagination_link_clickHandler(event) {
        event.preventDefault();

        let path = event.target.href; //
        let page = Global.getURLParameter(path, 'page');

        if (typeof page !== 'undefined') {
            jQuery.ajax({
                url: jQuery(this).attr('action'),
                type: 'POST',
                data: {'page': getURLParameter(path, 'page')},

                success: function (json) {
                    if (json.result) {
                        window.history.pushState({route: path}, "DISMART", path);
                        jQuery("#articles-list").replaceWith(articles);
                        Index.initPaginator();
                        jQuery(window).scrollTop(0);
                    }
                }
            });
        }
    }
}

Index.initPaginator();