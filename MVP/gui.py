# Modern OpenCV Viewer for Person Tracker Engine
# Enhanced interface with modern features and controls

import cv2
import numpy as np
import os
import time
import argparse
from ultralytics import YOLO
from fer import FER
from engine import PersonTrackerEngine

class ModernPersonTrackerViewer:
    def __init__(self, source='webcam', youtube_url=None, webcam_id=0, conf=0.4):
        self.source = source
        self.youtube_url = youtube_url
        self.webcam_id = webcam_id
        self.conf = conf
        
        # UI State
        self.is_fullscreen = False
        self.is_paused = False
        self.window_name = "Person Tracker - Modern View"
        
        # Colors (BGR format for OpenCV)
        self.colors = {
            'primary': (255, 165, 0),      # Orange
            'secondary': (0, 255, 255),    # Cyan
            'success': (0, 255, 0),        # Green
            'danger': (0, 0, 255),         # Red
            'warning': (0, 255, 255),      # Yellow
            'info': (255, 255, 255),       # White
            'dark': (40, 40, 40),          # Dark gray
            'overlay': (0, 0, 0, 128)      # Semi-transparent black
        }
        
        # Initialize models
        self.init_models()
        
        # Initialize video source
        self.init_video_source()
        
        # Initialize tracker engine
        self.tracker_engine = PersonTrackerEngine(
            self.person_model, 
            self.face_model, 
            self.emotion_detector, 
            conf=conf
        )

    def init_models(self):
        """Initialize YOLO models and emotion detector"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("🚀 Loading AI Models...")
        
        # Load person detection model
        person_onnx_path = os.path.join(current_dir, 'models', 'yolov8n.onnx')
        if os.path.exists(person_onnx_path):
            print("✅ Loading ONNX person detection model")
            self.person_model = YOLO(person_onnx_path, task='detect')
        else:
            print("⚠️ ONNX not found, loading PyTorch model")
            self.person_model = YOLO('yolov8n.pt')
        
        # Load face detection model
        face_onnx_path = os.path.join(current_dir, 'models', 'yolov8n-face-lindevs.onnx')
        if os.path.exists(face_onnx_path):
            print("✅ Loading ONNX face detection model")
            self.face_model = YOLO(face_onnx_path, task='detect')
        else:
            face_pt_path = os.path.join(current_dir, 'models', 'archive', 'yolov8n-face-lindevs.pt')
            if os.path.exists(face_pt_path):
                print("⚠️ Loading PyTorch face detection model")
                self.face_model = YOLO(face_pt_path)
            else:
                raise FileNotFoundError("No face detection model found!")
        
        # Initialize emotion detector
        print("🎭 Loading emotion detection model")
        self.emotion_detector = FER()
        print("✅ All models loaded successfully!")

    def init_video_source(self):
        """Initialize video capture source"""
        if self.source == 'youtube':
            from ARCHIVE.DetectAndTrack import get_video_stream_url
            stream_url = get_video_stream_url(self.youtube_url)
            if not stream_url:
                raise ValueError("Failed to get YouTube video URL")
            self.cap = cv2.VideoCapture(stream_url)
        else:
            self.cap = cv2.VideoCapture(self.webcam_id)
        
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video source: {self.source}")

    def draw_modern_overlay(self, frame, fps, total_persons, paused=False):
        """Draw modern UI overlay with glass morphism effect"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Create semi-transparent background for header
        header_height = 90
        cv2.rectangle(overlay, (0, 0), (w, header_height), self.colors['dark'], -1)
        
        # Apply transparency for header (lighter tint for better text visibility)
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Title in top left with glow effect
        title = "PERSON TRACKER - AI VISION"
        title_font = cv2.FONT_HERSHEY_DUPLEX
        title_scale = 1.0
        title_thickness = 2
        title_y = 35
        
        # Draw title with glow effect
        cv2.putText(frame, title, (22, title_y+2), title_font, title_scale, (0, 0, 0), title_thickness+2)  # Shadow
        cv2.putText(frame, title, (20, title_y), title_font, title_scale, self.colors['primary'], title_thickness)
        
        # Source indicator below title (smaller)
        source_text = f"Source: {'YouTube' if self.source == 'youtube' else 'Webcam'}"
        source_y = title_y + 25
        cv2.putText(frame, source_text, (20, source_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['secondary'], 1)
        
        # Person count below source
        person_text = f"Persons: {total_persons}"
        person_y = source_y + 20
        cv2.putText(frame, person_text, (20, person_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 1)
        
        # FPS indicator in top right
        fps_text = f"FPS: {fps:.1f}"
        fps_w, _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        fps_x = w - fps_w - 20
        cv2.putText(frame, fps_text, (fps_x, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['success'], 2)
        
        # Pause indicator in top right below FPS
        if paused:
            pause_text = "|| PAUSED"
            pause_w, _ = cv2.getTextSize(pause_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            pause_x = w - pause_w - 20
            cv2.putText(frame, pause_text, (pause_x, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['warning'], 2)
        
        # Controls help in middle bottom
        controls_y = h - 25
        controls = [
            "[F] Fullscreen",
            "[SPACE] Pause/Play", 
            "[Q] Quit"
        ]
        
        # Calculate total width of controls text
        total_controls_width = 0
        control_widths = []
        for control in controls:
            text_w, _ = cv2.getTextSize(control, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            control_widths.append(text_w)
            total_controls_width += text_w
        
        # Add spacing between controls (30px each)
        total_controls_width += 30 * (len(controls) - 1)
        
        # Create overlay for controls background
        controls_overlay = frame.copy()
        
        # Create a more precise background box for controls with padding
        padding_x = 20
        padding_y = 10
        controls_bg_x1 = (w - total_controls_width) // 2 - padding_x
        controls_bg_x2 = (w + total_controls_width) // 2 + padding_x
        controls_bg_y1 = controls_y - 20 - padding_y
        controls_bg_y2 = h - 5
        
        # Draw background box with outline for controls
        cv2.rectangle(controls_overlay, (controls_bg_x1, controls_bg_y1), (controls_bg_x2, controls_bg_y2), self.colors['dark'], -1)
        # Add subtle outline
        cv2.rectangle(controls_overlay, (controls_bg_x1, controls_bg_y1), (controls_bg_x2, controls_bg_y2), (80, 80, 80), 1)
        
        # Apply transparency for controls background
        frame = cv2.addWeighted(controls_overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw control text on top of the background
        x_offset = (w - total_controls_width) // 2
        for i, control in enumerate(controls):
            cv2.putText(frame, control, (x_offset, controls_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 1)
            x_offset += control_widths[i] + 30
        
        return frame

    def draw_enhanced_detections(self, frame, person_emotions):
        """Draw enhanced bounding boxes and emotion labels"""
        # This method is called after the engine processes the frame
        # The engine already draws basic bounding boxes, we'll enhance them
        return frame

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        try:
            if self.is_fullscreen:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                print("🖥️ Switched to fullscreen mode")
            else:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(self.window_name, 1280, 720)
                print("🪟 Switched to windowed mode")
        except Exception as e:
            print(f"⚠️ Fullscreen toggle not supported: {e}")
            # Fallback - just resize window
            cv2.resizeWindow(self.window_name, 1280, 720)

    def handle_keypress(self, key):
        """Handle keyboard input"""
        if key == ord('f') or key == ord('F'):
            self.toggle_fullscreen()
        elif key == ord(' '):  # Spacebar
            self.is_paused = not self.is_paused
            status = "paused" if self.is_paused else "resumed"
            print(f"⏯️ Video {status}")
        elif key == ord('q') or key == ord('Q') or key == 27:  # 'q' or Escape
            print("👋 Exiting application...")
            return False
        return True

    def run(self):
        """Main application loop"""
        print(f"🎬 Starting Person Tracker Viewer")
        print(f"📹 Source: {self.source}")
        if self.source == 'youtube':
            print(f"🔗 URL: {self.youtube_url}")
        
        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)
        
        # Set window properties (if available)
        try:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        except:
            pass
        
        last_frame = None
        running = True
        
        print("\n" + "="*60)
        print("🎮 CONTROLS:")
        print("   [F] - Toggle Fullscreen")
        print("   [SPACE] - Pause/Resume")
        print("   [Q] - Quit Application")
        print("="*60)
        while running:
            if not self.is_paused:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️ End of video stream or camera disconnected")
                    break
                last_frame = frame.copy()
                
                # Process frame through tracker engine only when not paused
                processed_frame, person_emotions, _, fps, total_persons = self.tracker_engine.process_frame(frame)
                
                # Apply modern overlay
                final_frame = self.draw_modern_overlay(processed_frame, fps, total_persons, self.is_paused)
            else:
                # When paused, use last frame without processing to save CPU
                if last_frame is not None:
                    # Just apply overlay to the last frame without any AI processing
                    final_frame = self.draw_modern_overlay(last_frame, 0.0, 0, self.is_paused)
                else:
                    # Create a black frame if no previous frame exists
                    black_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                    final_frame = self.draw_modern_overlay(black_frame, 0.0, 0, self.is_paused)
                
                # Sleep a bit when paused to reduce CPU usage
                time.sleep(0.1)
            
            # Display frame
            cv2.imshow(self.window_name, final_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_keypress(key):
                running = False
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Application closed successfully")

def main():
    parser = argparse.ArgumentParser(description='Modern Person Tracker Viewer')
    parser.add_argument('--source', type=str, default='webcam', 
                       choices=['webcam', 'youtube'], 
                       help='Source type: "webcam" or "youtube"')
    parser.add_argument('--youtube_url', type=str, 
                       default='https://youtu.be/su33E1lreMc?si=b2ritLiv6uCMKOx3',
                       help='YouTube URL if source is youtube')
    parser.add_argument('--webcam_id', type=int, default=0, 
                       help='Webcam device ID if source is webcam')
    parser.add_argument('--conf', type=float, default=0.4, 
                       help='Confidence threshold for detection')
    
    args = parser.parse_args()
    
    try:
        viewer = ModernPersonTrackerViewer(
            source=args.source,
            youtube_url=args.youtube_url,
            webcam_id=args.webcam_id,
            conf=args.conf
        )
        viewer.run()
    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure all required models are available and dependencies are installed")

if __name__ == "__main__":
    main()
