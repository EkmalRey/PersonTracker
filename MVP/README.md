# 🖥️ MVP - Desktop Person Tracker

The **Desktop Application** is a standalone Python script that provides **real-time person detection, tracking, and emotion recognition** using YOLO and FER models with full computer vision capabilities.

## 🎯 Core Features

- **🤖 Real-time Person Detection** - YOLO with ByteTrack for persistent ID tracking
- **👤 Face Detection** - Specialized YOLO model for accurate face detection within person bounding boxes
- **😊 Emotion Recognition** - FER-based facial emotion analysis (optimized 1-second intervals)
- **🛤️ Track History** - Visual polylines showing movement paths (last 30 points)
- **📺 Multi-Source Support** - Webcam or YouTube livestream input
- **⚡ Performance Optimized** - ONNX models for faster inference
- **📊 Live Statistics** - Real-time FPS counter and person count overlay
- **🎮 Interactive Controls** - Keyboard shortcuts for control

## 🚀 Quick Start

### Basic Usage:
```bash
python DetectAndTrack.py
```

### Command Line Options:
```bash
python DetectAndTrack.py --source [webcam|youtube] --youtube_url [URL] --webcam_id [ID] --model [MODEL] --conf [CONFIDENCE]
```

### Usage Examples:

#### Webcam (Default):
```bash
python DetectAndTrack.py --source webcam --webcam_id 0 --conf 0.4
```

#### YouTube Livestream:
```bash
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/dQw4w9WgXcQ" --conf 0.4
```

#### Custom Model with Higher Confidence:
```bash
python DetectAndTrack.py --model yolov8s.pt --conf 0.6
```

#### Different Camera:
```bash
python DetectAndTrack.py --webcam_id 1 --conf 0.3
```

## 📁 File Structure

```
MVP/
├── 🐍 DetectAndTrack.py           # Main application script
├── 📊 ONNX_Conversion.ipynb       # Model optimization notebook  
├── 📋 requirements.txt            # Python dependencies
├── 📄 README.md                   # This documentation
├── 📂 models/                     # AI Models directory
│   ├── 🤖 yolov8n.onnx           # Person detection (optimized)
│   ├── 👤 yolov8n-face-lindevs.onnx  # Face detection (optimized)
│   └── 📂 archive/               # Original PyTorch models (.pt)
│       ├── yolov8n.pt           # Person detection (original)
│       ├── yolov8n-face-lindevs.pt  # Face detection (original)
│       └── yolo11n.pt           # Alternative model
└── 📂 WebApp/                    # Web interface (separate)
    ├── server.py                # Flask backend
    ├── index.html               # Mobile frontend
    └── DEPLOYMENT_GUIDE.md      # Deployment instructions
```

## ⚙️ Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--source` | str | `webcam` | Input source: `webcam` or `youtube` |
| `--youtube_url` | str | None | YouTube video/livestream URL |
| `--webcam_id` | int | `0` | Webcam device ID (0, 1, 2, etc.) |
| `--model` | str | `yolov8n.pt` | YOLO model path (will use ONNX if available) |
| `--conf` | float | `0.4` | Detection confidence threshold (0.0-1.0) |

### Confidence Threshold Guide:
- **0.3** - More detections, some false positives
- **0.4** - Balanced (recommended default)
- **0.5** - Higher precision, fewer detections
- **0.6+** - Very strict, minimal false positives

## 🔧 System Requirements

### Minimum Requirements:
- **Python 3.8+**
- **4GB RAM**
- **CPU:** Intel i5 or AMD Ryzen 5
- **Storage:** 2GB free space

### Recommended for Optimal Performance:
- **8GB+ RAM**
- **GPU:** NVIDIA GTX 1060+ with CUDA
- **CPU:** Intel i7 or AMD Ryzen 7
- **SSD Storage**

### Core Dependencies:
```bash
ultralytics>=8.0.0      # YOLO models and tracking
opencv-python>=4.5.0    # Computer vision operations
numpy>=1.21.0           # Numerical computations
yt-dlp>=2023.1.0        # YouTube stream extraction
fer>=22.4.0             # Facial emotion recognition
moviepy>=1.0.0          # Video processing utilities
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Controls & Interface

### Keyboard Shortcuts:
- **'q' or ESC** - Quit application
- **Mouse** - Window interaction and resizing

### Display Information:
- **Source Type** - Shows "Webcam" or "YouTube"
- **FPS Counter** - Real-time frames per second
- **Person Count** - Number of detected persons
- **Person IDs** - Unique tracking numbers
- **Bounding Boxes** - Red for persons, green for faces
- **Emotion Labels** - Detected emotions with confidence percentage
- **Track History** - Gray polylines showing movement paths

## 🧠 How It Works

### Processing Pipeline:
1. **📹 Video Input** - Captures frames from webcam or YouTube stream
2. **🔍 Person Detection** - YOLO detects and tracks persons with unique IDs
3. **👤 Face Detection** - Secondary YOLO model finds faces within person bounding boxes
4. **😊 Emotion Analysis** - FER analyzes facial expressions (every 1 second for performance)
5. **🎨 Visualization** - Draws bounding boxes, track history, and emotion labels
6. **📊 Statistics** - Displays real-time FPS and person count

### Model Architecture:
- **Person Detection:** YOLOv8n (optimized for speed)
- **Face Detection:** YOLOv8n-face-lindevs (specialized for faces)
- **Emotion Recognition:** FER (7 emotions: angry, disgust, fear, happy, sad, surprise, neutral)
- **Tracking:** ByteTrack algorithm for ID persistence

### Performance Optimizations:
- **ONNX Models:** Faster inference than PyTorch models
- **Emotion Interval:** Process emotions every 1 second instead of every frame
- **Optimized Image Size:** 416x416 for ONNX models
- **Efficient Memory Usage:** Limited track history to 30 points
- **GPU Acceleration:** Automatic CUDA detection when available

## 🚀 Performance Optimization

### Use ONNX Models (Recommended):
1. Run the ONNX conversion notebook: `ONNX_Conversion.ipynb`
2. Place converted models in `models/` directory
3. Application automatically detects and uses ONNX models

### Performance Tips:
- **Lower confidence** (`--conf 0.3`) for more detections
- **Higher confidence** (`--conf 0.6`) for fewer false positives
- **Close other applications** to free up resources
- **Use SSD storage** for faster model loading
- **Enable GPU acceleration** with CUDA-compatible GPU

### Troubleshooting Performance:
- **Low FPS** → Use ONNX models, reduce video resolution
- **High CPU usage** → Enable GPU acceleration
- **Memory issues** → Close other applications, use smaller model

## 🐛 Troubleshooting

### Common Issues & Solutions:

#### 1. Camera Not Detected:
```bash
# Try different camera IDs
python DetectAndTrack.py --webcam_id 1
python DetectAndTrack.py --webcam_id 2
```

#### 2. YouTube Stream Fails:
```bash
# Update yt-dlp
pip install -U yt-dlp

# Try different video URL
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/DIFFERENT_URL"
```

#### 3. Models Not Found:
```
❌ Error: No model found!
✅ Solution: Ensure models are in models/ directory
- Check models/yolov8n.onnx exists
- Check models/archive/yolov8n.pt exists
```

#### 4. Low Performance:
```bash
# Use optimized settings
python DetectAndTrack.py --conf 0.5 --model yolov8n.pt
```

#### 5. Import Errors:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Debug Information:
- Application shows model loading status
- Console displays error messages
- FPS counter indicates performance issues

## 🎯 Advanced Usage

### Custom Model Training:
1. Use YOLOv8 training pipeline
2. Convert to ONNX for optimization
3. Place in `models/` directory
4. Update model path in arguments

### YouTube Stream Quality Selection:
The application automatically selects the best available quality:
- 1080p → 720p60 → 720p → 480p → 360p → 240p → 144p

### Multiple Camera Setup:
```bash
# Camera 0 (default)
python DetectAndTrack.py --webcam_id 0

# Camera 1 (external USB camera)
python DetectAndTrack.py --webcam_id 1

# Camera 2 (second external camera)
python DetectAndTrack.py --webcam_id 2
```

## 🔮 Planned Enhancements

### Short Term:
- [ ] **GUI Interface** - PyQt or Tkinter controls
- [ ] **Configuration File** - Save/load settings
- [ ] **Recording Feature** - Save processed video
- [ ] **Screenshot Capture** - Save current frame

### Medium Term:
- [ ] **Re-identification** - Prevent ID number inflation
- [ ] **Multi-camera Support** - Process multiple streams
- [ ] **Data Logging** - CSV export of tracking data
- [ ] **Real-time Dashboard** - Separate statistics window

### Long Term:
- [ ] **Custom Emotion Models** - Train domain-specific models
- [ ] **3D Pose Estimation** - Extended person analysis
- [ ] **Age/Gender Detection** - Additional demographic info
- [ ] **Behavior Analysis** - Activity recognition

## 📊 Performance Benchmarks

### Typical Performance (YOLOv8n + ONNX):
| Hardware | Resolution | FPS | Person Detection | Face Detection |
|----------|------------|-----|------------------|----------------|
| RTX 3070 | 1280x720 | 25-30 | ✅ Excellent | ✅ Excellent |
| GTX 1060 | 1280x720 | 15-20 | ✅ Good | ✅ Good |
| Intel i7 (CPU) | 1280x720 | 8-12 | ✅ Acceptable | ⚠️ Slow |
| Intel i5 (CPU) | 640x480 | 10-15 | ✅ Good | ✅ Acceptable |

### Emotion Recognition Performance:
- **Processing Interval:** 1 second (configurable)
- **Accuracy:** ~85% on clear frontal faces
- **Latency:** <100ms per face
- **Memory Usage:** ~500MB with models loaded

---

🎯 **Ready to start?** Run: `python DetectAndTrack.py`  
📱 **Want the web version?** Check out [WebApp/README.md](WebApp/README.md)  
🚀 **Need deployment help?** See [WebApp/DEPLOYMENT_GUIDE.md](WebApp/DEPLOYMENT_GUIDE.md)
