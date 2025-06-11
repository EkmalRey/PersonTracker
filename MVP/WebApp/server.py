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
from engine import PersonTrackerEngine

app = Flask(__name__)

models_dir = os.path.join(current_dir, '..', 'models')

# Load models
person_model_path = os.path.join(models_dir, 'yolov8n.onnx')
face_model_path = os.path.join(models_dir, 'yolov8n-face-lindevs.onnx')

person_model = YOLO(person_model_path, task='detect')
face_model = YOLO(face_model_path, task='detect')
emotion_detector = FER()

# Initialize tracking and emotion detection engine
person_tracker_engine = PersonTrackerEngine(
    person_model=person_model,
    face_model=face_model,
    emotion_detector=emotion_detector,
    conf=0.4,
    emotion_interval=1.0
)

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
    try:
        # Decode the image from the request
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])
        np_image = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Call the PersonTrackerEngine process_frame method
        draw_frame, person_emotions, last_emotion_time, current_fps, total_persons = person_tracker_engine.process_frame(frame)

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
