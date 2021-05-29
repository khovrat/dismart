var value = 3;

function changeFontSize(my_value) {
    if (my_value > 0) {
        window.value++;
    } else {
        window.value--;
    }
    if ((my_value < 0 && window.value > 0) || (my_value > 0 && window.value < 9)) {
        var all = document.getElementsByTagName("*");
        for (var i = 0, max = all.length; i < max; i++) {
            if (all[i].className.includes("scale")) {
                var old_val = window.getComputedStyle(all[i], null).getPropertyValue('font-size');
                if (old_val) {
                    var old_num = parseFloat(old_val);
                    var matches_alpha = old_val.match(/[A-Za-z]+/);
                    if (old_num && matches_alpha) {
                        if (matches_alpha[0] === "px") {
                            var new_val = old_num + my_value;
                            all[i].style.fontSize = new_val + matches_alpha[0];
                        }
                    }
                }
            }
        }
    }
}