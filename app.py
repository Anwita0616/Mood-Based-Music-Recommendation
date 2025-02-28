import os
import cv2
import random
import numpy as np
from flask import Flask, render_template, request, jsonify
from deepface import DeepFace
import googleapiclient.discovery

app = Flask(__name__)

# Define extended mood categories
extended_moods = {
    "happy": ["Happy", "Relaxed", "Energetic"],
    "sad": ["Sad", "Tired", "Bored"],
    "neutral": ["Neutral", "Focus", "Chill"]
}

# Function to map DeepFace emotions to extended moods
def get_extended_mood(emotion):
    if emotion in ["happy", "surprise"]:
        return random.choice(extended_moods["happy"])
    elif emotion in ["sad", "fear", "disgust"]:
        return random.choice(extended_moods["sad"])
    else:  # "neutral" or other emotions
        return random.choice(extended_moods["neutral"])

# YouTube API Key to get songs from youtube
YOUTUBE_API_KEY = "Your Youtube API Key"

def get_song_recommendation(mood):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    search_query = f"{mood} mood music playlist"
    
    request = youtube.search().list(
        q=search_query,
        part="snippet",
        type="video",
        maxResults=5
    )
    
    response = request.execute()
    
    video_list = [
        {
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        for item in response.get("items", [])
    ]

    return video_list

# Serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Handle mood detection from uploaded webcam images
@app.route("/detect_mood", methods=["POST"])
def detect_mood():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"].read()
    image_array = np.frombuffer(image_file, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Perform mood detection
    result = DeepFace.analyze(image, actions=["emotion"], enforce_detection=False)
    detected_emotion = result[0]["dominant_emotion"]

    # Map to extended mood
    extended_mood = get_extended_mood(detected_emotion)

    # Get song recommendations
    song_recommendations = get_song_recommendation(extended_mood)

    return jsonify({
        "mood": extended_mood,
        "songs": song_recommendations
    })

if __name__ == "__main__":
    app.run(debug=True)
