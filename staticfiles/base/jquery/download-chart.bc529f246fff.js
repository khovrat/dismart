$('#download-chart').on('click', function () {
    var canvas = document.getElementById('chart');
    var img = canvas.toDataURL("image/png");
    var link = document.createElement('a');
    link.download = "chart.png";
    link.href = img;
    link.target = 'blank_';
    link.click();
});