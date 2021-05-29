onload = function () {
    if ('speechSynthesis' in window) {
        var synth = speechSynthesis;
        var flag = false;

        var playEle = document.querySelector('#play');
        var pauseEle = document.querySelector('#pause');
        var stopEle = document.querySelector('#stop');

        playEle.addEventListener('click', onClickPlay);
        pauseEle.addEventListener('click', onClickPause);
        stopEle.addEventListener('click', onClickStop);

        function onClickPlay() {
            if (!flag) {
                flag = true;
                utterance = new SpeechSynthesisUtterance(
                    document.querySelector('.article').textContent);
                utterance.voice = synth.getVoices()[0];
                utterance.onend = function () {
                    flag = false;
                };
                synth.speak(utterance);
            }
            if (synth.paused) {
                synth.resume();
            }
        }

        function onClickPause() {
            if (synth.speaking && !synth.paused) {
                synth.pause();
            }
        }

        function onClickStop() {
            if (synth.speaking) {
                flag = false;
                synth.cancel();
            }
        }
    }
}
