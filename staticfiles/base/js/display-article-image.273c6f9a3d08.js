function readButtonItemURL(input) {
    if (input.files && input.files[0]) {
        document.getElementById(input.labels[0].innerHTML).src = URL.createObjectURL(input.files[0]);
    }
}