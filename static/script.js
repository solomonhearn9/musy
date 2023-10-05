// This example uses MediaRecorder to record from a live audio stream,
// and uses the resulting blob as a source for an audio element.
// The relevant functions in use are:
// navigator.mediaDevices.getUserMedia -> to get audio stream from microphone
// MediaRecorder (constructor) -> create MediaRecorder instance for a stream
// MediaRecorder.ondataavailable -> event to listen to when the recording is ready
// MediaRecorder.start -> start recording
// MediaRecorder.stop -> stop recording (this will generate a blob of data)
// URL.createObjectURL -> to create a URL from a blob, which we can use as audio src

var recordButton, stopButton, recorder;

window.onload = function () {
  recordButton = document.getElementById('record');
  stopButton = document.getElementById('stop');

  // get audio stream from user's mic
  navigator.mediaDevices.getUserMedia({
    audio: true
  })
  .then(function (stream) {
    recordButton.disabled = false;
    recordButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    recorder = new MediaRecorder(stream);

    // listen to dataavailable, which gets triggered whenever we have
    // an audio blob available
    recorder.addEventListener('dataavailable', onRecordingReady);
  });
};

function startRecording() {
  recordButton.disabled = true;
  stopButton.disabled = false;

  recorder.start();
}

function stopRecording() {
  recordButton.disabled = false;
  stopButton.disabled = true;

  // Stopping the recorder will eventually trigger the `dataavailable` event and we can complete the recording process
  recorder.stop();
}


function onRecordingReady(e) {
    var audio = document.getElementById('audio');
    audio.src = URL.createObjectURL(e.data);
    //audio.play();

    // Upload the audio file to the server
    uploadAudio(e.data);
}

function uploadAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())  // Assuming server sends back the filepath as plain text
    .then(filepath => {
        // Send filepath to synthesize_speech endpoint
        fetch('/synthesize_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filepath: filepath })
        })
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => {
            const audioContext = new AudioContext();
            audioContext.decodeAudioData(arrayBuffer, buffer => {
                const source = audioContext.createBufferSource();
                source.buffer = buffer;
                source.connect(audioContext.destination);
                source.start(0);
            });
        })
        .catch(error => console.error('Synthesis error:', error));
    })
    .catch(error => console.error('Upload error:', error));
}
