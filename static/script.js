// This example uses MediaRecorder to record from a live audio stream,
// and uses the resulting blob as a source for an audio element.
// The relevant functions in use are:
// navigator.mediaDevices.getUserMedia -> to get audio stream from microphone
// MediaRecorder (constructor) -> create MediaRecorder instance for a stream
// MediaRecorder.ondataavailable -> event to listen to when the recording is ready
// MediaRecorder.start -> start recording
// MediaRecorder.stop -> stop recording (this will generate a blob of data)
// URL.createObjectURL -> to create a URL from a blob, which we can use as audio src

var recordSpeechButton, stopSpeechButton, recorder;
var recordPitchButton, stopPitchButton, recorder2;
window.onload = function () {
  recordSpeechButton = document.getElementById('recordSpeech');
  stopSpeechButton = document.getElementById('stopRecordSpeech');
  recordPitchButton = document.getElementById('recordPitch');
  stopPitchButton = document.getElementById('stopRecordPitch');

  // get audio stream from user's mic
  navigator.mediaDevices.getUserMedia({
    audio: true
  })
  .then(function (stream) {
    // Enable both record buttons
    recordSpeechButton.disabled = false;
    recordPitchButton.disabled = false;

    // Event listeners for speech recording
    recordSpeechButton.addEventListener('click', startRecording);
    stopSpeechButton.addEventListener('click', stopRecording);
    
    // Event listeners for pitch recording
    recordPitchButton.addEventListener('click', startPitchRecording);
    stopPitchButton.addEventListener('click', stopPitchRecording);

    recorder = new MediaRecorder(stream);
    recorder.addEventListener('dataavailable', onRecordingReady);
  
    recorder2 = new MediaRecorder(stream);
    recorder2.addEventListener('dataavailable', onPitchRecordingReady);
  })
  .catch(function (err) {
    console.error("Error accessing microphone: ", err);
    alert("Error accessing microphone. Please ensure you have granted the necessary permissions.");
  });
};

//start and stop speech recording
function startRecording() {
    // Stop any existing recorder
    if (recorder2) {
      recorder2.stop();
  }

  recordSpeechButton.disabled = true;
  stopSpeechButton.disabled = false;
  recordPitchButton.disabled = true;
  stopPitchButton.disabled = true;

  recorder2.stop();
  recorder.start();
}

function stopRecording() {
  recordSpeechButton.disabled = false;
  stopSpeechButton.disabled = true;
  recordPitchButton.disabled = false;  // Enable pitch recording button
  stopPitchButton.disabled = true;

  recorder.stop();
}

var lastPitchSentTime = null;

var audioContext, microphoneStream, pitchProcessor, recordedChunks = [];

function startPitchRecording() {
    // Stop any existing recorder
    if (recorder) {
        recorder.stop();
    }

    recordPitchButton.disabled = true;
    stopPitchButton.disabled = false;
    recordSpeechButton.disabled = true;
    stopSpeechButton.disabled = true;

    // Initialize audio context
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    // Get microphone stream
    navigator.mediaDevices.getUserMedia({ audio: true }).then(function(stream) {
        microphoneStream = audioContext.createMediaStreamSource(stream);
        pitchProcessor = audioContext.createScriptProcessor(1024, 1, 1);
        var mediaRecorder = new MediaRecorder(stream);

        microphoneStream.connect(pitchProcessor);
        pitchProcessor.connect(audioContext.destination);

        pitchProcessor.onaudioprocess = function(event) {
            var inputData = event.inputBuffer.getChannelData(0);
            // For now, we'll just log the raw audio data
            // Later, you can integrate aubio's pitch detection here for real-time feedback
            console.log(inputData);
        };

        mediaRecorder.ondataavailable = function(event) {
            recordedChunks.push(event.data);
        };

        mediaRecorder.onstop = function() {
            var blob = new Blob(recordedChunks, { type: 'audio/wav' });
            // Send the recorded audio to the Flask backend for pitch detection
            var formData = new FormData();
            formData.append('audio', blob);
            fetch('/detect_pitch', {
                method: 'POST',
                body: formData
            }).then(response => response.json()).then(data => {
                console.log(data); // This will log the detected pitches from the backend
            });
        };

        // Start the media recorder after a delay
        setTimeout(function() {
            mediaRecorder.start();
            // Stop recording after a set duration (e.g., 5 seconds)
            setTimeout(function() {
                mediaRecorder.stop();
            }, 5000);
        }, 1000);
    }).catch(function(err) {
        console.error('Error accessing the microphone', err);
    });
}



function stopPitchRecording() {
  recordPitchButton.disabled = false;
  stopPitchButton.disabled = true;
  recordSpeechButton.disabled = false;
  stopSpeechButton.disabled = true;

  // Disconnect and stop the audio processing
  pitchProcessor.disconnect();
  microphoneStream.disconnect();
  pitchProcessor.onaudioprocess = null;
}


function detectPitch(audioBlob) {

  const formData = new FormData();
 
  formData.append('audio', audioBlob, 'audio.wav');

  fetch('/detect_pitch', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      console.log("Detected Pitches:", data.pitches);
  })
  .catch(error => console.error('Error detecting pitch:', error));
  return jsonify(pitches=pitches, confidences=confidences)

}


function savePitchToLocal(pitch) {
  localStorage.setItem("lastDetectedPitch", JSON.stringify(pitch));
}

function getLastSavedPitch() {
  return JSON.parse(localStorage.getItem("lastDetectedPitch"));
}

function onRecordingReady(e) {
  var audio = document.getElementById('audio');
  audio.src = URL.createObjectURL(e.data);

  
  uploadAudio(e.data);
}

function onPitchRecordingReady(e) {
  var audio = document.getElementById('audio');
    audio.src = URL.createObjectURL(e.data);

    const formData = new FormData();
    formData.append('audio', e.data, 'audio.wav');

    // Send audio data to server for pitch detection
    fetch('/detect_pitch', {
        method: 'POST',
        body: formData
    })
    // .then(response => response.json())
    .then(data => {
        // Display the detected pitch on the UI
        displayPitch(data.pitch);
    });
}



function displayPitch(pitch) {
  var targetPitch = 440; // Example target pitch (A4)
    var pitchDisplay = document.getElementById('pitchDisplay');
    
    if (!pitch) {
        pitchDisplay.textContent = "No pitch detected.";
        return;
    }

    if (pitch > targetPitch) {
        pitchDisplay.textContent = "Detected Pitch: " + pitch + ". You're playing sharp. Try to lower the pitch slightly.";
    } else if (pitch < targetPitch) {
        pitchDisplay.textContent = "Detected Pitch: " + pitch + ". You're playing flat. Try to raise the pitch slightly.";
    } else {
        pitchDisplay.textContent = "Detected Pitch: " + pitch + ". Perfect! You're on pitch.";
    }
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
