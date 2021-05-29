var descriptions = document.getElementsByClassName("clamp-this-module");
for (var i = 0; i < descriptions.length; i++) {
    $clamp(descriptions[i], {clamp: 4});
}