var descriptions = document.getElementsByClassName("clamp-this-module");
for (var i = 0; i < descriptions.length; i++) {
    $clamp(descriptions[i], {clamp: 3});
}
var titles = document.getElementsByClassName("clamp-this-module-one");
for (var j = 0; j < titles.length; j++) {
    $clamp(titles[j], {clamp: 1});
}
