// Expose globally your audio_context, the recorder instance and audio_stream
var audio_context;
var recorder;
var audio_stream;

/**
    ** Patch the APIs for every browser that supports them and check
    * if getUserMedia is supported on the browser.*/

// This function allows the user to send pre-recorded voice messages stored on
// the serve
function sendMessage(e){
    alert(e);
    $.ajax({
          type: 'POST',
            url: serverName + '/mic_test_pre',
          data: e
      });
}


// This function initializes the audio stream, and alerts the user if the microphone is not
// supported
function Initialize() {
    try {
        // Monkeypatch for AudioContext, getUserMedia and URL
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.mediaDevices.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        // Store the instance of AudioContext globally
        audio_context = new AudioContext;
        console.log('Audio context is ready !');
        console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
        alert('No web audio support in this browser!');
    }
}

//
// Starts the recording process by requesting the access to the microphone.
// Then, if granted proceeds to initialize the library and store the stream.
// It only stops when the method stopRecording is triggered.

function startRecording() {
    // Access the Microphone using the navigator.getUserMedia method to obtain a stream
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        // Expose the stream to be accessible globally
        audio_stream = stream;
        // Create the MediaStreamSource for the Recorder library
        var input = audio_context.createMediaStreamSource(stream);
        console.log('Media stream succesfully created');

        // Initialize the Recorder Library
        recorder = new Recorder(input);
        console.log('Recorder initialised');

        // Start recording !
        recorder && recorder.record();
        console.log('Recording...');

        // Disable Record button and enable stop button !
        document.getElementById("start-btn").disabled = true;
        document.getElementById("stop-btn").disabled = false;
    }, function (e) {
        console.error('No live audio input: ' + e);
    });
}


//Stops the recording process. The method expects a callback as first
//argument (function) executed once the AudioBlob is generated and it
//receives the same Blob as first argument. The second argument is
//optional and specifies the format to export the blob either wav or mp3

function stopRecording(callback, AudioFormat) {
    // Stop the recorder instance
    recorder && recorder.stop();
    console.log('Stopped recording.');

    // Stop the getUserMedia Audio Stream !
    audio_stream.getAudioTracks()[0].stop();

    // Disable Stop button and enable Record button !
    document.getElementById("start-btn").disabled = false;
    document.getElementById("stop-btn").disabled = true;

    // Use the Recorder Library to export the recorder Audio as a .wav file
    // The callback provided in the stop recording method receives the blob
    if(typeof(callback) == "function"){
        recorder && recorder.exportWAV(function (blob) {
            callback(blob);

            // Clear the Recorder to start again !
            recorder.clear();
        }, (AudioFormat || "audio/wav"));
    }
}

// Initialize everything once the window loads
window.onload = function(){
    // Prepare and check if requirements are filled
    Initialize();

    // Handle on start recording button
    document.getElementById("start-btn").addEventListener("click", function(){
        startRecording();
    }, false);

    // Handle on stop recording button
    document.getElementById("stop-btn").addEventListener("click", function(){
        // Use wav format
        var _AudioFormat = "audio/wav";
        //var AudioFormat = "audio/mpeg";

        stopRecording(function(AudioBLOB){
            //sends wav file to Cloud for forwarding to Pi
            var formData = new FormData();
            formData.append('file', AudioBLOB, 'securityMessage'+'.wav');

            var http = new XMLHttpRequest();
            http.open("POST", serverName + "/mic_test");
                    http.send(formData);
            }, _AudioFormat);
    }, false);
};


