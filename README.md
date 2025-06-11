# 🎯 AI Person Tracker with Emotion Detection

A comprehensive computer vision project that combines **person detection**, **tracking**, and **emotion recognition** using state-of-the-art AI models. Available as both desktop application and modern web-based solution.

## ✨ Key Features

- **🤖 Person Detection & Tracking** - YOLO with ByteTrack for multi-person tracking with persistent IDs
- **👤 Face Detection** - Specialized YOLO model for accurate face detection within person bounding boxes
- **😊 Emotion Recognition** - Real-time facial emotion analysis using FER (optimized 1-second intervals)
- **📺 Multi-Source Input** - Supports webcam and YouTube livestreams
- **🛤️ Track History** - Visual trails showing person movement paths with polylines
- **📱 Web Interface** - Mobile-first web app perfect for demos and exhibitions
- **⚡ ONNX Optimization** - Faster inference with optimized ONNX models
- **📊 Live Statistics** - Real-time FPS counter and person count display

## 🏗️ Project Architecture

```
📂 PersonTracker/
├── 📄 README.md                     # Main project documentation
├── 📂 MVP/                          # Core application directory
│   ├── 🐍 DetectAndTrack.py         # Desktop application (standalone)
│   ├── 📊 ONNX_Conversion.ipynb     # Model optimization notebook
│   ├── 📋 requirements.txt          # Python dependencies
│   ├── 📄 README.md                 # Desktop app documentation
│   ├── 📂 models/                   # AI Models storage
│   │   ├── 🤖 yolov8n.onnx          # Optimized person detection
│   │   ├── 👤 yolov8n-face-lindevs.onnx  # Optimized face detection
│   │   └── 📂 archive/             # Original PyTorch models (.pt)
│   └── 📂 WebApp/                  # Web-based interface
│       ├── 🌐 server.py             # Flask backend with AI processing
│       ├── 📱 index.html            # Mobile-optimized frontend
│       ├── 📄 README.md             # WebApp documentation
│       └── 🚀 DEPLOYMENT_GUIDE.md   # Production deployment guide
└── 📂 data/                         # Optional: datasets and outputs
```

## 🚀 Quick Start Guide

### 🖥️ Desktop Application

#### 1. Setup Environment
```bash
cd MVP
pip install -r requirements.txt
```

#### 2. Basic Usage (Webcam)
```bash
python DetectAndTrack.py
```

#### 3. YouTube Stream
```bash
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/your-stream-url"
```

#### 4. Advanced Configuration
```bash
python DetectAndTrack.py --source webcam --webcam_id 0 --conf 0.4 --model yolov8n.pt
```

### 📱 Web Application

#### 1. Start Server
```bash
cd MVP/WebApp
python server.py
```

#### 2. Access Interface
- **Local:** http://localhost:8080
- **Mobile:** http://YOUR_IP:8080 (replace with your computer's IP)

#### 3. Grant Permissions
- Tap "🚀 Start Tracking"
- Allow camera access when prompted
- Point camera at people to see live AI detection

## 🛠️ System Requirements

### Minimum Requirements:
- **Python 3.8+**
- **4GB RAM**
- **CPU:** Intel i5 or AMD Ryzen 5
- **Storage:** 2GB free space
- **Camera:** For webcam mode

### Recommended for Optimal Performance:
- **8GB+ RAM**
- **GPU:** NVIDIA GTX 1060 or better (CUDA support)
- **CPU:** Intel i7 or AMD Ryzen 7
- **SSD Storage**

### Core Dependencies:
```
ultralytics>=8.0.0    # YOLO models
opencv-python>=4.5.0  # Computer vision
numpy>=1.21.0         # Numerical operations
yt-dlp>=2023.1.0      # YouTube stream extraction
fer>=22.4.0           # Facial emotion recognition
flask>=2.0.0          # Web framework (WebApp only)
```

## 📚 Documentation

| Document | Description | Target Audience |
|----------|-------------|-----------------|
| **[MVP README](MVP/README.md)** | Desktop application details, usage examples | Developers, researchers |
| **[WebApp README](MVP/WebApp/README.md)** | Web interface features, mobile usage | End users, demo presenters |
| **[Deployment Guide](MVP/WebApp/DEPLOYMENT_GUIDE.md)** | Production deployment with Cloudflare | DevOps, system admins |
| **[ONNX Conversion](MVP/ONNX_Conversion.ipynb)** | Model optimization tutorial | ML engineers |

## 🎯 Usage Examples

### Desktop Examples:
```bash
# Basic webcam with default settings
python DetectAndTrack.py

# High confidence detection
python DetectAndTrack.py --conf 0.6

# Different camera
python DetectAndTrack.py --webcam_id 1

# YouTube livestream
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/dQw4w9WgXcQ"

# Custom model with specific confidence
python DetectAndTrack.py --model yolov8s.pt --conf 0.5
```

### Web Application Examples:
```bash
# Local development
cd MVP/WebApp && python server.py

# Production with custom host/port
cd MVP/WebApp && python server.py --host 0.0.0.0 --port 5000

# With debug mode
cd MVP/WebApp && FLASK_ENV=development python server.py
```

## 🌐 Deployment Options

| Option | Use Case | Complexity | Cost |
|--------|----------|------------|------|
| **Local Development** | Testing, development | ⭐ | Free |
| **Local Network** | Demos, presentations | ⭐⭐ | Free |
| **Cloudflare Tunnel** | Public demos, sharing | ⭐⭐⭐ | Free |
| **Cloud VPS** | Production, scaling | ⭐⭐⭐⭐ | $5-50/month |
| **Serverless** | Auto-scaling, enterprise | ⭐⭐⭐⭐⭐ | Pay-per-use |

## 🎪 Perfect for Demonstrations

The web interface is ideal for:
- **📱 Tech Exhibitions** - Interactive AI demos
- **🏫 Educational Presentations** - Live computer vision examples  
- **🔬 Research Showcases** - Real-time emotion analysis
- **🎉 Social Events** - Fun interactive experiences
- **🏢 Business Demos** - Client presentations

## 🔮 Roadmap & Future Enhancements

### Short Term:
- [ ] **Re-Identification** - Prevent ID inflation across frames
- [ ] **GUI Controls** - Desktop app with start/stop, settings
- [ ] **Data Export** - Save tracking logs and emotion data
- [ ] **Performance Dashboard** - Real-time system metrics

### Medium Term:
- [ ] **Multi-Camera Support** - Handle multiple video inputs
- [ ] **Advanced Analytics** - Emotion trends and heatmaps
- [ ] **REST API** - Integrate with other applications
- [ ] **Database Integration** - Store historical data

### Long Term:
- [ ] **Machine Learning Pipeline** - Custom model training
- [ ] **Real-time Streaming** - WebRTC for ultra-low latency
- [ ] **Edge Deployment** - Run on mobile devices directly
- [ ] **3D Pose Estimation** - Extended person analysis

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Report Bugs** - Create detailed issue reports
2. **💡 Feature Requests** - Suggest new functionality
3. **🔧 Code Contributions** - Submit pull requests
4. **📖 Documentation** - Improve guides and examples
5. **🧪 Testing** - Test on different devices and scenarios

### Development Setup:
```bash
git clone https://github.com/yourusername/PersonTracker.git
cd PersonTracker/MVP
pip install -r requirements.txt
python DetectAndTrack.py --help
```

## 📄 License & Usage

This project is available for:
- ✅ **Educational Use** - Learning and teaching
- ✅ **Research Projects** - Academic and commercial research
- ✅ **Personal Projects** - Individual use and development
- ✅ **Demo/Exhibition** - Public demonstrations

## 🆘 Support & Troubleshooting

### Common Issues:
- **Camera not detected** → Try different `--webcam_id` values
- **YouTube stream fails** → Update `yt-dlp`: `pip install -U yt-dlp`
- **Low FPS** → Use ONNX models or lower `--conf` threshold
- **Models not found** → Check `models/` directory and file paths

### Getting Help:
1. Check the relevant README file for your use case
2. Review the troubleshooting sections
3. Search existing issues on GitHub
4. Create a new issue with detailed information

---

🎯 **Ready to try it?** Start with the desktop app: `cd MVP && python DetectAndTrack.py`  
📱 **Want the web version?** Check out the [WebApp README](MVP/WebApp/README.md)!
```

### 4. Web Application:
```bash
cd WebApp
python server.py
# Open browser to http://localhost:8080
```

## 📱 Web Interface Features

- **Mobile-First Design** - Optimized for smartphones and tablets
- **Real-Time Processing** - Live camera feed with AI processing
- **Touch-Friendly Controls** - Large buttons and intuitive interface
- **Live Statistics** - Shows FPS and person count in real-time
- **Responsive Canvas** - Auto-scales to device screen size

## 🔧 Requirements

- **Python 3.8+**
- **OpenCV** (`opencv-python`)
- **YOLO** (`ultralytics`)
- **NumPy** (`numpy`)
- **YouTube Support** (`yt-dlp`)
- **Emotion Recognition** (`fer`)
- **Web Interface** (`flask`)

Install all dependencies:
```bash
pip install -r MVP/requirements.txt
```

## 📖 Documentation

- **[MVP README](MVP/README.md)** - Desktop application details
- **[WebApp Deployment Guide](MVP/WebApp/DEPLOYMENT_GUIDE.md)** - Production deployment with Cloudflare Tunnel
- **[ONNX Conversion Notebook](MVP/ONNX_Conversion.ipynb)** - Model optimization guide

## 🎯 Usage Examples

### Basic Webcam Detection:
```bash
cd MVP
python DetectAndTrack.py
```

### High Confidence Detection:
```bash
python DetectAndTrack.py --conf 0.6
```

### YouTube Live Stream:
```bash
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/dQw4w9WgXcQ"
```

## 🚀 Deployment Options

1. **Local Development** - Run on localhost for testing
2. **Cloudflare Tunnel** - Deploy to custom domain (see deployment guide)
3. **Cloud VPS** - Deploy on DigitalOcean, AWS, or Google Cloud
4. **Mobile Demo** - Perfect for exhibitions and presentations

## 🔮 Roadmap

- [ ] **Re-Identification** - Prevent ID numbers from growing infinitely
- [ ] **GUI Controls** - Start/stop, source switching, FPS control
- [ ] **Multiple Camera Support** - Handle multiple video inputs
- [ ] **Data Export** - Save tracking data and emotion logs
- [ ] **Advanced Analytics** - Emotion history and trends
- [ ] **API Endpoints** - RESTful API for integration

## 🤝 Contributing

Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is available for educational and research purposes.

---

✅ **Quick Test:** Make sure all models are downloaded and `yt-dlp` is installed before running YouTube streams.
