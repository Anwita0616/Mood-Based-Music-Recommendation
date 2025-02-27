const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureButton = document.getElementById("capture");
const moodResult = document.getElementById("mood-result");
const songsList = document.getElementById("songs-list");

let stream = null;
let moodDetected = false; // Track if a mood has been detected

// Function to start the webcam
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(mediaStream => {
            stream = mediaStream;
            video.srcObject = stream;
        })
        .catch(error => console.error("Error accessing webcam:", error));
}

// Function to stop the webcam
function stopCamera() {
    if (stream) {
        let tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}

// Start webcam when page loads
startCamera();

// Capture image and send to backend
captureButton.addEventListener("click", () => {
    if (moodDetected) {
        location.reload(); // Reload the page if mood has already been detected
        return;
    }

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append("image", blob, "mood.jpg");

        fetch("/detect_mood", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            moodResult.textContent = data.mood;
            songsList.innerHTML = "";
            data.songs.forEach(song => {
                let li = document.createElement("li");
                let link = document.createElement("a");
                link.href = song.url;
                link.textContent = song.title;
                link.target = "_blank";
                li.appendChild(link);
                songsList.appendChild(li);
            });

            stopCamera(); // Stop the camera

            // Replace video with mood image
            const moodImage = document.createElement("img");
            moodImage.src = `/static/images/${data.mood}.jpg`;  // Image path
            moodImage.alt = data.mood;
            moodImage.width = video.width;
            moodImage.height = video.height;

            // Replace video with image
            video.replaceWith(moodImage);

            moodDetected = true; // Set flag to indicate mood detected
        })
        .catch(error => console.error("Error detecting mood:", error));
    });
});
