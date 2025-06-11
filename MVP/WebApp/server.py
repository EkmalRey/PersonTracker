from flask import Flask, send_from_directory, request, jsonify
import os
import cv2
import numpy as np
import base64
import sys

# Add the parent directory to the Python path first
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from ultralytics import YOLO
from fer import FER
from collections import defaultdict
import time
from DetectAndTrack import process_frame_for_web, FPS

app = Flask(__name__)

models_dir = os.path.join(current_dir, '..', 'models')

# Load models
person_model_path = os.path.join(models_dir, 'yolov8n.onnx')
face_model_path = os.path.join(models_dir, 'yolov8n-face-lindevs.onnx')

person_model = YOLO(person_model_path, task='detect')
face_model = YOLO(face_model_path, task='detect')
emotion_detector = FER()

# Initialize tracking and emotion detection variables
fps_counter = FPS()
track_history = defaultdict(lambda: [])
processed_ids = set()
person_emotions = defaultdict(lambda: {"emotion": "Unknown", "confidence": 0.0, "last_update": 0})
last_emotion_time = time.time()
emotion_interval = 1.0  # 1 second interval

# Serve the index.html file
@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

# Serve static files (if any)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(os.path.dirname(__file__), path)

# Process video frames sent from the client and return the processed image
@app.route('/process_frame', methods=['POST'])
def process_frame():
    global last_emotion_time, person_emotions
    
    try:
        # Decode the image from the request
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])
        np_image = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Call the process_frame_for_web function
        draw_frame, person_emotions, last_emotion_time, current_fps, total_persons = process_frame_for_web(
            frame, person_model, face_model, emotion_detector, fps_counter, 
            track_history, processed_ids, person_emotions, last_emotion_time, emotion_interval
        )

        # Encode the processed frame to send back to the client
        _, buffer = cv2.imencode('.jpg', draw_frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')

        return jsonify({ 
            'success': True, 
            'processed_image': f'data:image/jpeg;base64,{processed_image}',
            'fps': current_fps,
            'total_persons': total_persons
        })
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) })

if __name__ == '__main__':
    # Run the server on port 8080 for easy Cloudflare Tunnel integration
    app.run(host='0.0.0.0', port=8080)
