
// static/js/record_audio.js

document.addEventListener('DOMContentLoaded', function() {
    let mediaRecorder;
    let audioChunks = [];

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function playAudio(audioUrl) {
        var audioPlayer = document.getElementById('botAudioPlayer');
        audioPlayer.src = audioUrl;
        audioPlayer.hidden = false; // Show the player
        audioPlayer.play(); // Start playback
    }
});
