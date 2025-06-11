from ultralytics import YOLO
import subprocess
import cv2
import numpy as np
import argparse
from collections import defaultdict
from threading import Thread
import time
import os
from fer import FER  # Import library FER untuk deteksi ekspresi wajah

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

class VideoStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = Thread(target=self.update, args=()).start()

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()
    
    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

class FPS:
    def __init__(self):
        self.prev_time = time.time()
        self.curr_time = 0
        self.frame_count = 0
        self.fps = 0
        self.update_interval = 1

    def update(self):
        self.frame_count += 1
        self.curr_time = time.time()
        time_diff = self.curr_time - self.prev_time
        
        if time_diff >= self.update_interval:
            self.fps = self.frame_count / time_diff
            self.frame_count = 0
            self.prev_time = self.curr_time
        
        return self.fps

def get_video_stream_url(youtube_url):
    formats = {
        "270": "1080",
        "311": "720p60",
        "232": "720p",
        "136": "720p",
        "135": "480p",
        "134": "360p",
        "133": "240p",
        "160": "144p"
    }
    for fmt in formats.keys():
        cmd = ["yt-dlp", "-g", "-f", fmt, youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        video_url = result.stdout.strip()
        if video_url:
            print(f"\r✅ Found video URL for {formats[fmt]}")
            return video_url
        else:
            print(f"\r❌ Format {formats[fmt]} not available, trying lower quality...")
    print("\r❌ No valid MP4 video format found.")
    return None

def main():
    parser = argparse.ArgumentParser(description='YOLO Object Tracking with YouTube or Webcam')
    parser.add_argument('--source', type=str, default='webcam', help='Source type: "webcam" or "youtube"')
    parser.add_argument('--youtube_url', type=str, default='https://youtu.be/su33E1lreMc?si=b2ritLiv6uCMKOx3', help='YouTube URL if source is youtube')
    parser.add_argument('--webcam_id', type=int, default=0, help='Webcam device ID if source is webcam')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.4, help='Confidence threshold')
    args = parser.parse_args()

    detect_and_track(args.source, args.youtube_url, args.webcam_id, args.model, args.conf)

def detect_and_track(source='webcam', youtube_url=None, webcam_id=0, model_path='yolov8n.pt', conf=0.4):
    print(f"Loading YOLO models...")

    # Try to use ONNX models first (faster inference)
    person_onnx_path = os.path.join(current_dir, 'models', 'yolov8n.onnx')
    face_onnx_path = os.path.join(current_dir, 'models', 'yolov8n-face-lindevs.onnx')

    # Load person detection model (ONNX first, then fallback to PyTorch from archive)
    if os.path.exists(person_onnx_path):
        print("✅ Using ONNX person detection model for faster inference")
        model = YOLO(person_onnx_path, task='detect')
    else:
        archive_model_path = os.path.join(current_dir, 'models', 'archive', model_path)
        if os.path.exists(archive_model_path):
            print(f"⚠️ ONNX not found, using PyTorch model from archive: {archive_model_path}")
            model = YOLO(archive_model_path)
        elif os.path.exists(model_path):
            print("⚠️ ONNX not found, using PyTorch person detection model")
            model = YOLO(model_path)
        else:
            print("❌ No model found! Please run ONNX conversion or check model paths")
            print("   Run: python convert_to_onnx.py")
            return

    # Load face detection model (ONNX first, then fallback to PyTorch from archive)
    if os.path.exists(face_onnx_path):
        print("✅ Using ONNX face detection model for faster inference")
        face_model = YOLO(face_onnx_path, task='detect')
    else:
        face_pt_path = os.path.join(current_dir, 'models', 'archive', 'yolov8n-face-lindevs.pt')
        if os.path.exists(face_pt_path):
            print("⚠️ Face ONNX not found, using PyTorch face detection model from archive")
            face_model = YOLO(face_pt_path)
        else:
            print("❌ No face detection model found!")
            print("   Please ensure yolov8n-face-lindevs model is in models/archive/")
            return

    # Initialize FER for facial expression recognition
    emotion_detector = FER()

    if source == 'youtube':
        stream_url = get_video_stream_url(youtube_url)
        if not stream_url:
            print("Failed to get YouTube video URL. Exiting.")
            return
        vs = VideoStream(stream_url)
    else:
        vs = VideoStream(webcam_id)

    fps_counter = FPS()
    track_history = defaultdict(lambda: [])
    frame_counter = 0
    running = True

    # Emotion processing timing - process every 1 second
    last_emotion_time = time.time()
    emotion_interval = 1.0  # 1 second interval

    # Menyimpan ID yang sudah diproses untuk info logging
    processed_ids = set()

    # Store last detected emotions for each person (persistent display)
    person_emotions = defaultdict(lambda: {"emotion": "Unknown", "confidence": 0.0, "last_update": 0})

    while running:
        ret, frame = vs.read()
        if not ret or frame is None:
            print("\n⚠️ Stream ended or failed.")
            break
        frame = cv2.resize(frame, (1280, 720))  # Larger frame for expo presentation

        result = model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            conf=conf,
            iou=0.5,
            imgsz=416,          # Optimized size for ONNX model
            stream=False,
            verbose=False       # Reduce console output for better performance
        )[0]

        draw_frame = frame.copy()
        total_person_detected = 0

        if result.boxes and hasattr(result.boxes, 'id') and result.boxes.id is not None:
            boxes = result.boxes.xywh.cpu()
            track_ids = result.boxes.id.int().cpu().tolist()
            total_person_detected = len(track_ids)

            for box, track_id in zip(boxes, track_ids):
                x_center, y_center, w, h = box
                x1 = int(x_center - w / 2)
                y1 = int(y_center - h / 2)
                x2 = int(x_center + w / 2)
                y2 = int(y_center + h / 2)

                cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(draw_frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                track = track_history[track_id]
                track.append((float(x_center), float(y_center)))
                if len(track) > 30:
                    track.pop(0)

                if len(track) > 1:
                    points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(draw_frame, [points], isClosed=False, color=(230, 230, 230), thickness=2)

                # Process emotions for all detected persons
                current_time = time.time()
                should_update_emotion = current_time - last_emotion_time >= emotion_interval

                y1_safe = max(0, y1)
                y2_safe = min(frame.shape[0], y2)
                x1_safe = max(0, x1)
                x2_safe = min(frame.shape[1], x2)

                if y2_safe > y1_safe and x2_safe > x1_safe:
                    person_roi = frame[y1_safe:y2_safe, x1_safe:x2_safe]
                    if person_roi.size > 0 and person_roi.shape[0] > 20 and person_roi.shape[1] > 20:
                        try:
                            faces_result = face_model(person_roi, conf=0.5, imgsz=320, verbose=False)[0]

                            if faces_result.boxes:
                                for box in faces_result.boxes.xyxy:
                                    fx1, fy1, fx2, fy2 = map(int, box)

                                    # Draw face rectangle
                                    cv2.rectangle(draw_frame, (fx1 + x1_safe, fy1 + y1_safe), 
                                                (fx2 + x1_safe, fy2 + y1_safe), (0, 255, 0), 2)
                                    cv2.putText(draw_frame, "Face", 
                                                (fx1 + x1_safe, fy1 + y1_safe - 10), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                                    # Update emotions if interval has passed
                                    if should_update_emotion:
                                        emotions = emotion_detector.detect_emotions(person_roi)
                                        if emotions:
                                            top = emotions[0]["emotions"]
                                            top_emotion = max(top.items(), key=lambda x: x[1])
                                            person_emotions[track_id]["emotion"] = top_emotion[0]
                                            person_emotions[track_id]["confidence"] = top_emotion[1]
                                            person_emotions[track_id]["last_update"] = current_time

                                    # Update last known face position
                                    person_emotions[track_id]["last_face"] = (fx1 + x1_safe, fy1 + y1_safe, fx2 + x1_safe, fy2 + y1_safe)

                        except Exception as e:
                            print(f"Error processing face detection: {e}")

                # Always display the last known emotion and face position for this person
                if track_id in person_emotions:
                    emotion_data = person_emotions[track_id]

                    # Display persistent emotion
                    emotion_x = x1
                    emotion_y = y2 + 30

                    if "last_face" in emotion_data:
                        fx1, fy1, fx2, fy2 = emotion_data["last_face"]
                        cv2.rectangle(draw_frame, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                        cv2.putText(draw_frame, "Face", (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        emotion_x = fx1
                        emotion_y = fy2 + 20

                    cv2.putText(draw_frame, f"Emotion: {emotion_data['emotion']} ({emotion_data['confidence']*100:.0f}%)", 
                                (emotion_x, emotion_y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if should_update_emotion:
                    last_emotion_time = current_time  # Update the last emotion processing time

        current_fps = fps_counter.update()
        source_text = f"Source: {'YouTube' if source == 'youtube' else 'Webcam'}"
        fps_text = f"FPS: {current_fps:.1f}"

        cv2.putText(draw_frame, source_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(draw_frame, fps_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(draw_frame, f"Total Persons: {total_person_detected}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow('Detect and Track', draw_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            running = False

        frame_counter += 1

    vs.stop()
    cv2.destroyAllWindows()
    print("\n✅ Detection and tracking completed.")

def process_frame_for_web(frame, person_model, face_model, emotion_detector, fps_counter, track_history, processed_ids, person_emotions, last_emotion_time, emotion_interval, conf=0.4):
    """
    Process a single frame for web application use
    Returns: (processed_frame, updated_person_emotions, updated_last_emotion_time, fps, total_persons)
    """
    current_time = time.time()
    should_update_emotion = current_time - last_emotion_time >= emotion_interval
    
    # Update last emotion time if interval passed
    if should_update_emotion:
        last_emotion_time = current_time
    
    # Resize frame for consistent processing
    frame = cv2.resize(frame, (1280, 720))
    
    result = person_model.track(
        source=frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[0],
        conf=conf,
        iou=0.5,
        imgsz=416,
        stream=False,
        verbose=False
    )[0]

    draw_frame = frame.copy()
    total_person_detected = 0

    if result.boxes and hasattr(result.boxes, 'id') and result.boxes.id is not None:
        boxes = result.boxes.xywh.cpu()
        track_ids = result.boxes.id.int().cpu().tolist()
        total_person_detected = len(track_ids)

        for box, track_id in zip(boxes, track_ids):
            x_center, y_center, w, h = box
            x1 = int(x_center - w / 2)
            y1 = int(y_center - h / 2)
            x2 = int(x_center + w / 2)
            y2 = int(y_center + h / 2)

            cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(draw_frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            track = track_history[track_id]
            track.append((float(x_center), float(y_center)))
            if len(track) > 30:
                track.pop(0)

            if len(track) > 1:
                points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(draw_frame, [points], isClosed=False, color=(230, 230, 230), thickness=2)

            y1_safe = max(0, y1)
            y2_safe = min(frame.shape[0], y2)
            x1_safe = max(0, x1)
            x2_safe = min(frame.shape[1], x2)

            if y2_safe > y1_safe and x2_safe > x1_safe:
                person_roi = frame[y1_safe:y2_safe, x1_safe:x2_safe]
                if person_roi.size > 0 and person_roi.shape[0] > 20 and person_roi.shape[1] > 20:
                    try:
                        faces_result = face_model(person_roi, conf=0.5, imgsz=320, verbose=False)[0]

                        if faces_result.boxes:
                            for box in faces_result.boxes.xyxy:
                                fx1, fy1, fx2, fy2 = map(int, box)

                                # Draw face rectangle
                                cv2.rectangle(draw_frame, (fx1 + x1_safe, fy1 + y1_safe), 
                                            (fx2 + x1_safe, fy2 + y1_safe), (0, 255, 0), 2)
                                cv2.putText(draw_frame, "Face", 
                                            (fx1 + x1_safe, fy1 + y1_safe - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                                # Update emotions if interval has passed
                                if should_update_emotion:
                                    emotions = emotion_detector.detect_emotions(person_roi)
                                    if emotions:
                                        top = emotions[0]["emotions"]
                                        top_emotion = max(top.items(), key=lambda x: x[1])
                                        person_emotions[track_id]["emotion"] = top_emotion[0]
                                        person_emotions[track_id]["confidence"] = top_emotion[1]
                                        person_emotions[track_id]["last_update"] = current_time

                                # Update last known face position
                                person_emotions[track_id]["last_face"] = (fx1 + x1_safe, fy1 + y1_safe, fx2 + x1_safe, fy2 + y1_safe)

                    except Exception as e:
                        print(f"Error processing face detection: {e}")

            # Always display the last known emotion and face position for this person
            if track_id in person_emotions:
                emotion_data = person_emotions[track_id]

                # Display persistent emotion
                emotion_x = x1
                emotion_y = y2 + 30

                if "last_face" in emotion_data:
                    fx1, fy1, fx2, fy2 = emotion_data["last_face"]
                    cv2.rectangle(draw_frame, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                    cv2.putText(draw_frame, "Face", (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    emotion_x = fx1
                    emotion_y = fy2 + 20

                cv2.putText(draw_frame, f"Emotion: {emotion_data['emotion']} ({emotion_data['confidence']*100:.0f}%)", 
                            (emotion_x, emotion_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    current_fps = fps_counter.update()
    fps_text = f"FPS: {current_fps:.1f}"
    
    cv2.putText(draw_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(draw_frame, f"Total Persons: {total_person_detected}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    return draw_frame, person_emotions, last_emotion_time, current_fps, total_person_detected


if __name__ == "__main__":
    main()
