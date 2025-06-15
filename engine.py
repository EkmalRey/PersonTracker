# Engine for detection and tracking
# This will be imported by GUI and WebApp/server.py

import cv2
import numpy as np
import time
from collections import defaultdict

class PersonTrackerEngine:
    def __init__(self, person_model, face_model, emotion_detector, conf=0.4, emotion_interval=1.0):
        self.person_model = person_model
        self.face_model = face_model
        self.emotion_detector = emotion_detector
        self.conf = conf
        self.emotion_interval = emotion_interval
        self.track_history = defaultdict(lambda: [])
        self.person_emotions = defaultdict(lambda: {"emotion": "Unknown", "confidence": 0.0, "last_update": 0})
        self.last_emotion_time = time.time()

    def process_frame(self, frame):
        current_time = time.time()
        should_update_emotion = current_time - self.last_emotion_time >= self.emotion_interval
        if should_update_emotion:
            self.last_emotion_time = current_time
        frame = cv2.resize(frame, (1280, 720))
        result = self.person_model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            conf=self.conf,
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
                track = self.track_history[track_id]
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
                            faces_result = self.face_model(person_roi, conf=0.5, imgsz=320, verbose=False)[0]
                            if faces_result.boxes:
                                for box in faces_result.boxes.xyxy:
                                    fx1, fy1, fx2, fy2 = map(int, box)
                                    cv2.rectangle(draw_frame, (fx1 + x1_safe, fy1 + y1_safe), (fx2 + x1_safe, fy2 + y1_safe), (0, 255, 0), 2)
                                    cv2.putText(draw_frame, "Face", (fx1 + x1_safe, fy1 + y1_safe - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                    if should_update_emotion:
                                        emotions = self.emotion_detector.detect_emotions(person_roi)
                                        if emotions:
                                            top = emotions[0]["emotions"]
                                            top_emotion = max(top.items(), key=lambda x: x[1])
                                            self.person_emotions[track_id]["emotion"] = top_emotion[0]
                                            self.person_emotions[track_id]["confidence"] = top_emotion[1]
                                            self.person_emotions[track_id]["last_update"] = current_time
                                    self.person_emotions[track_id]["last_face"] = (fx1 + x1_safe, fy1 + y1_safe, fx2 + x1_safe, fy2 + y1_safe)
                        except Exception as e:
                            print(f"Error processing face detection: {e}")                # Only show emotions when face is detected and emotion data exists
                if track_id in self.person_emotions:
                    emotion_data = self.person_emotions[track_id]
                    # Only display emotion if we have face data
                    if "last_face" in emotion_data and emotion_data["emotion"] != "Unknown":
                        fx1, fy1, fx2, fy2 = emotion_data["last_face"]
                        # Draw face bounding box
                        cv2.rectangle(draw_frame, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                        cv2.putText(draw_frame, "Face", (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        # Draw emotion text near the face
                        emotion_x = fx1
                        emotion_y = fy2 + 25
                        cv2.putText(draw_frame, f"Emotion: {emotion_data['emotion']} ({emotion_data['confidence']*100:.0f}%)", 
                                   (emotion_x, emotion_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # FPS calculation (simple)
        current_fps = 0.0
        if not hasattr(self, '_fps_counter'):
            self._fps_counter = {'prev_time': time.time(), 'frame_count': 0, 'fps': 0.0}
        self._fps_counter['frame_count'] += 1
        now = time.time()
        diff = now - self._fps_counter['prev_time']
        if diff >= 1.0:
            self._fps_counter['fps'] = self._fps_counter['frame_count'] / diff
            self._fps_counter['frame_count'] = 0
            self._fps_counter['prev_time'] = now
        current_fps = self._fps_counter['fps']
        return draw_frame, self.person_emotions, self.last_emotion_time, current_fps, total_person_detected
