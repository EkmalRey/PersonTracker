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
from collections import defaultdict
import pandas as pd

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

    print(f"Loading YOLO model: {args.model}")
    if os.path.exists(args.model):
        model_path = args.model
    else:
        model_path = os.path.join(current_dir, 'models', args.model)
        
    model = YOLO(model_path)
    face_model = YOLO(os.path.join(current_dir, 'models', 'yolov8n-face-lindevs.pt'))

    # Initialize FER for facial expression recognition
    emotion_detector = FER()

    if args.source == 'youtube':
        stream_url = get_video_stream_url(args.youtube_url)
        if not stream_url:
            print("Failed to get YouTube video URL. Exiting.")
            return
        vs = VideoStream(stream_url)
    else:
        vs = VideoStream(args.webcam_id)

    fps_counter = FPS()
    track_history = defaultdict(lambda: [])
    frame_counter = 0
    running = True

    # Menyimpan skor emosi untuk setiap ID
    emotion_scores = defaultdict(lambda: defaultdict(list))

    # Menyimpan ID yang sudah diproses
    processed_ids = set()

    # Siapkan CSV log untuk menulis secara bertahap
    log_file = 'emotion_scores_log.csv'
    if not os.path.exists(log_file):
        pd.DataFrame(columns=['ID', 'Emotion', 'Score']).to_csv(log_file, index=False)


    while running:
        ret, frame = vs.read()
        if not ret or frame is None:
            print("\n⚠️ Stream ended or failed.")
            break
        frame = cv2.resize(frame, (640, 360))

        result = model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            conf=args.conf,
            iou=0.5,
            imgsz=640,
            stream=False
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

                if frame_counter % 1 == 0:
                    y1_safe = max(0, y1)
                    y2_safe = min(frame.shape[0], y2)
                    x1_safe = max(0, x1)
                    x2_safe = min(frame.shape[1], x2)

                    if y2_safe > y1_safe and x2_safe > x1_safe:
                        person_roi = frame[y1_safe:y2_safe, x1_safe:x2_safe]
                        if person_roi.size > 0 and person_roi.shape[0] > 20 and person_roi.shape[1] > 20:
                            try:
                                faces_result = face_model(person_roi, conf=0.5)[0]  # Deteksi wajah dengan YOLO

                                if faces_result.boxes:
                                    for box in faces_result.boxes.xyxy:
                                        x1, y1, x2, y2 = map(int, box)
                                        cv2.rectangle(draw_frame, (x1 + x1_safe, y1 + y1_safe), 
                                                    (x2 + x1_safe, y2 + y1_safe), (0, 255, 0), 2)
                                        cv2.putText(draw_frame, "Face", 
                                                    (x1 + x1_safe, y1 + y1_safe - 10), 
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                                    
                                        # Deteksi ekspresi wajah
                                        # Deteksi semua emosi
                                        emotions = emotion_detector.detect_emotions(person_roi)
                                        if emotions:
                                            top = emotions[0]["emotions"]
                                            for emo_label, emo_score in top.items():
                                                # Jika ID baru, tandai sebagai sudah diproses
                                                if track_id not in processed_ids:
                                                    processed_ids.add(track_id)
                                                    print(f"[INFO] Detected new person with ID: {track_id}")

                                                # Simpan skor emosi ke dalam struktur data dan langsung log ke CSV
                                                for emo_label, emo_score in top.items():
                                                    emotion_scores[track_id][emo_label].append(emo_score)
                                                    
                                                    # Tulis ke log file secara langsung
                                                    with open(log_file, 'a') as f:
                                                        f.write(f"{track_id},{emo_label},{emo_score:.4f}\n")


                                            # Menampilkan emosi tertinggi
                                            top_emotion = max(top.items(), key=lambda x: x[1])
                                            cv2.putText(draw_frame, f"Emotion: {top_emotion[0]} ({top_emotion[1]*100:.2f}%)", 
                                                        (x1 + x1_safe, y2 + y1_safe + 20), 
                                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            except Exception as e:
                                print(f"Error processing face detection: {e}")


        current_fps = fps_counter.update()
        source_text = f"Source: {'YouTube' if args.source == 'youtube' else 'Webcam'}"
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

    # Buat DataFrame dari skor emosi
    results = []
    for track_id, emotions in emotion_scores.items():
        avg_scores = {emo: sum(scores) / len(scores) if scores else 0 for emo, scores in emotions.items()}
        avg_scores['ID'] = track_id
        results.append(avg_scores)

    df_results = pd.DataFrame(results)
    df_results = df_results[['ID'] + [col for col in df_results.columns if col != 'ID']]  # Pastikan kolom ID di awal
    df_results.to_csv('emotion_scores_summary.csv', index=False)
    print("\n📁 Emotion summary saved to 'emotion_scores_summary.csv'")
    print(df_results)


if __name__ == "__main__":
    main()
