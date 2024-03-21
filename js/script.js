// script.js
document.getElementById('startBtn').addEventListener('click', startRecording);
document.getElementById('stopBtn').addEventListener('click', stopRecording);

let mediaRecorder;
let audioChunks = [];

function startRecording() {
    console.log('startRecording')
    navigator.mediaDevices.getUserMedia({
        audio: true
        })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();

            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        });
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { 'type' : 'audio/wav'}); //; codecs=opus' });
        audioChunks = [];

        sendAudioToServer(audioBlob);
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    };
}

function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob);

    fetch('http://localhost:3003/upload', { method: 'POST', body: formData })
        .then(response => response.blob())
        .then(audioFromServer => {
            const audioUrl = URL.createObjectURL(audioFromServer);
            document.getElementById('responseAudio').src = audioUrl;
            document.getElementById('responseAudio').play();
        })
        .catch(console.error);
}

function __log(e, data) {
    log.innerHTML += "\n" + e + " " + (data || '');
}