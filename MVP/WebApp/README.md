# 📱 WebApp - Mobile Person Tracker

A **mobile-first web application** that brings AI person tracking and emotion detection to smartphones and tablets through a responsive web interface with server-side AI processing.

## ✨ Features

- **📱 Mobile-Optimized** - Designed specifically for smartphones and tablets
- **🎥 Live Camera Access** - Uses device camera (front/back) via WebRTC
- **🤖 Server-Side AI** - YOLO + FER processing on backend for better performance
- **📊 Real-Time Stats** - Live FPS, person count, and status display
- **🎨 Modern UI** - Beautiful gradient design with smooth animations
- **👆 Touch-Friendly** - Large buttons and intuitive mobile controls
- **🌐 Web-Based** - No app installation required, works in any browser
- **⚡ Optimized Performance** - Efficient frame processing and display

## 🚀 Quick Start

### 1. Start the Server:
```bash
cd WebApp
python server.py
```

### 2. Access the App:
- **Local:** http://localhost:8080
- **Mobile:** http://YOUR_IP:8080 (replace with your computer's IP address)
- **Network:** Use `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to find your IP

### 3. Grant Camera Permissions:
- Tap "🚀 Start Tracking" button
- Allow camera access when prompted by browser
- Point camera at people to see live AI detection in action

## 📁 File Structure

```
WebApp/
├── 🌐 server.py              # Flask backend with AI processing
├── 📱 index.html             # Mobile-optimized frontend interface
├── 📄 README.md              # This documentation
└── 🚀 DEPLOYMENT_GUIDE.md    # Production deployment instructions
```

## 🛠️ Technical Architecture

### Frontend (`index.html`):
- **📹 Camera Capture** - Accesses device camera via WebRTC APIs
- **📤 Frame Transmission** - Sends video frames to server as base64 encoded images
- **🖼️ Real-Time Display** - Shows processed frames with AI detection overlays
- **📊 Statistics UI** - Displays FPS, person count, and connection status
- **📱 Responsive Design** - Adapts to any screen size and orientation

### Backend (`server.py`):
- **📥 Frame Processing** - Receives frames via POST requests
- **🤖 AI Inference** - Runs YOLO person detection and face detection models
- **😊 Emotion Recognition** - FER analysis every 1 second (performance optimized)
- **📤 Response** - Returns processed frame with bounding boxes and emotion labels
- **📊 Statistics** - Provides real-time FPS and detection count data

## 🎮 User Interface

### Header Section:
- **🎯 App Title** - "Person Tracker" with emoji
- **📊 Live Statistics Dashboard**:
  - 📊 FPS: Real-time processing speed
  - 👥 Persons: Current detection count
  - 🎥 Status: Connection and processing state

### Camera View:
- **📺 Full-Screen Canvas** - Responsive video display that adapts to device
- **🎨 Real-Time Processing** - Live AI detection overlay with bounding boxes
- **⏳ Loading Indicator** - Visual feedback during camera initialization
- **🔄 Auto-scaling** - Maintains aspect ratio on all devices

### Control Panel:
- **🚀 Start Tracking** - Begin camera capture and AI processing
- **🛑 Stop** - End tracking session and release camera resources
- **📝 Status Messages** - Clear user feedback and instructions
- **🎨 Modern Styling** - Gradient buttons with hover effects

## 📱 Mobile-Specific Features

### Responsive Design:
- **📏 Auto-scaling Canvas** - Fits any screen size perfectly
- **👆 Touch Optimization** - Large, easy-to-tap interactive elements
- **🔄 Orientation Support** - Works in both portrait and landscape modes
- **✨ Smooth Animations** - Modern UI transitions and feedback

### Camera Support:
- **📷 Camera Selection** - Automatic front/back camera detection
- **🎯 High Resolution** - Prefers 1280x720 capture when available
- **⚡ Real-time Processing** - Minimal latency between capture and display
- **🛡️ Error Handling** - Clear permission and error messages

### Performance Optimizations:
- **🖼️ Image Compression** - 80% JPEG quality for faster transmission
- **⏱️ Frame Rate Control** - Adaptive processing based on device capabilities
- **💾 Memory Management** - Efficient canvas and image handling
- **🔄 Background Processing** - Non-blocking UI updates

## 🔧 Configuration Options

### Server Settings (`server.py`):
```python
# Network Configuration
host='0.0.0.0'          # Accept connections from any device
port=8080               # Web server port (changeable)

# AI Model Settings
conf=0.4                # Detection confidence threshold
emotion_interval=1.0    # Emotion processing interval in seconds

# Performance Settings
max_content_length=16MB # Maximum upload size for safety
```

### Frontend Settings (`index.html`):
```javascript
// Camera Configuration
video: { 
    facingMode: 'user',           // Start with front camera
    width: { ideal: 1280 },       // Preferred capture width
    height: { ideal: 720 }        // Preferred capture height
}

// Image Quality and Performance
canvas.toDataURL('image/jpeg', 0.8)  # 80% JPEG compression
requestAnimationFrame(processFrames) # Smooth 60fps updates
```

## 🌐 Network Access & Deployment

### Local Network Access:
1. **Find Your Computer's IP Address:**
   ```bash
   # Windows PowerShell
   ipconfig | Select-String "IPv4"
   
   # Mac/Linux Terminal
   ifconfig | grep "inet "
   ```

2. **Access from Mobile Device:**
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

3. **QR Code Generation (Optional):**
   - Use any QR code generator to create a code for your URL
   - Perfect for demos and easy mobile access

### Public Deployment:
For internet-accessible deployment, see **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for:
- 🌐 Cloudflare Tunnel setup (free)
- 🔒 Custom domain configuration
- ⚡ Production optimization tips
- 🛡️ Security considerations

## 🔌 API Reference

### GET `/`
- **Purpose:** Serve the main web application
- **Response:** HTML interface with embedded CSS and JavaScript

### POST `/process_frame`
- **Purpose:** Process uploaded video frame with AI models
- **Content-Type:** `application/json`
- **Input Format:** 
  ```json
  {
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  }
  ```
- **Success Response:** 
  ```json
  {
    "success": true,
    "processed_image": "data:image/jpeg;base64,...",
    "fps": 15.2,
    "total_persons": 3
  }
  ```
- **Error Response:**
  ```json
  {
    "success": false,
    "error": "Error message description"
  }
  ```

## 🐛 Troubleshooting Guide

### Camera Access Issues:
- **🔒 HTTPS Required** - Modern browsers require HTTPS for camera access on non-localhost domains
- **🚫 Permission Denied** - Clear browser data/cookies and try again
- **📱 Multiple Tabs** - Close other tabs that might be using the camera
- **🔄 Browser Restart** - Sometimes required after permission changes

### Performance Issues:
- **🐌 Low FPS** - Reduce image quality or resolution in settings
- **⏰ High Latency** - Check network connection speed and stability
- **💻 Server Overload** - Monitor CPU/GPU usage on server machine
- **📱 Device Performance** - Test on different devices to isolate issues

### Connection Problems:
- **🔥 Firewall Blocking** - Check Windows Firewall or antivirus settings
- **🌐 Network Error** - Verify IP address and port accessibility
- **🔗 CORS Issues** - Server includes proper CORS headers
- **📡 WiFi Issues** - Ensure both devices are on same network

### Browser Compatibility:
- **✅ Supported:** Chrome, Firefox, Safari, Edge (modern versions)
- **❌ Limited:** Internet Explorer, older mobile browsers
- **📱 Mobile:** iOS Safari 11+, Android Chrome 67+

## 🎪 Perfect for Exhibitions

### Use Cases:
- **🏫 Educational Demonstrations** - Interactive AI learning experiences
- **🔬 Research Showcases** - Real-time computer vision examples  
- **🎉 Tech Exhibitions** - Engaging public AI demonstrations
- **📊 Business Presentations** - Live emotion analysis demos
- **🎮 Interactive Installations** - Fun, engaging user experiences

### Exhibition Setup Tips:
1. **📱 QR Code Display** - Generate QR code for easy mobile access
2. **📶 Stable Network** - Use reliable WiFi or mobile hotspot
3. **🔋 Backup Plan** - Have offline demo ready as fallback
4. **📱 Device Testing** - Test on various phones and tablets beforehand
5. **📋 Clear Instructions** - Provide simple, visual user guidance
6. **🖥️ Display Screen** - Show live statistics on separate monitor

## 🚀 Performance Optimization

### Server-Side Optimizations:
- **⚡ ONNX Models** - Use optimized ONNX models for faster inference
- **🎯 Frame Skipping** - Process every Nth frame for better performance
- **💾 Caching** - Cache model predictions for repeated detections
- **🖥️ GPU Acceleration** - Utilize CUDA when available

### Client-Side Optimizations:
- **📉 Reduce Frame Rate** - Lower transmission rate for slower connections
- **🗜️ Image Compression** - Adjust JPEG quality based on network speed
- **⏭️ Frame Skipping** - Skip frames during processing on client side
- **⏳ Loading States** - Better UX with loading indicators and progress

### Network Optimizations:
- **📦 WebSocket Upgrade** - Consider WebSockets for real-time communication
- **🔄 Connection Pooling** - Reuse HTTP connections when possible
- **📊 Bandwidth Monitoring** - Adapt quality based on connection speed
- **🎯 Edge Computing** - Deploy closer to users for lower latency

---

🌟 **Ready for public deployment?** Check out **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for production setup with custom domains and HTTPS!

🎯 **Want to try locally?** Run `python server.py` and visit http://localhost:8080 on your phone!
- **AI Inference** - Runs YOLO person detection and face detection
- **Emotion Recognition** - FER analysis every 1 second (optimized)
- **Response** - Returns processed frame with bounding boxes and labels

## 🎮 User Interface

### Header:
- **🎯 App Title** - "Person Tracker"
- **📊 Live Stats** - FPS, Person Count, Status

### Camera View:
- **Full-Screen Canvas** - Responsive video display
- **Real-Time Processing** - Live AI detection overlay
- **Loading Indicator** - Camera initialization feedback

### Controls:
- **🚀 Start Tracking** - Begin camera capture and processing
- **🛑 Stop** - End tracking and release camera
- **Status Messages** - User feedback and instructions

## 📱 Mobile Features

### Responsive Design:
- **Auto-scaling canvas** - Fits any screen size
- **Touch optimization** - Large, easy-to-tap buttons
- **Portrait/landscape** - Works in any orientation
- **Smooth animations** - Modern UI transitions

### Camera Support:
- **Front/back camera** - Automatic device selection
- **High resolution** - 1280x720 preferred capture
- **Real-time processing** - Minimal latency
- **Error handling** - Clear permission messages

## 🔧 Configuration

### Server Settings (server.py):
```python
# Network configuration
host='0.0.0.0'    # Accept connections from any device
port=8080         # Web server port

# AI Model settings
conf=0.4          # Detection confidence threshold
emotion_interval=1.0  # Emotion processing interval (seconds)
```

### Frontend Settings (index.html):
```javascript
// Camera configuration
video: { 
    facingMode: 'user',           // Front camera default
    width: { ideal: 1280 },       // Preferred width
    height: { ideal: 720 }        // Preferred height
}

// Image quality
canvas.toDataURL('image/jpeg', 0.8)  // 80% JPEG quality
```

## 🌐 Network Access

### Local Network:
1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. Access from mobile device:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

### Public Access:
For public deployment, see **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for:
- Cloudflare Tunnel setup
- Custom domain configuration
- Production optimization
- Security considerations

## 🔍 API Endpoints

### GET `/`
- **Purpose:** Serve main application
- **Response:** HTML interface

### POST `/process_frame`
- **Purpose:** Process video frame
- **Input:** `{ "image": "data:image/jpeg;base64,..." }`
- **Output:** 
  ```json
  {
    "success": true,
    "processed_image": "data:image/jpeg;base64,...",
    "fps": 15.2,
    "total_persons": 3
  }
  ```

## 🐛 Troubleshooting

### Camera Access Issues:
- **HTTPS Required** - Modern browsers require HTTPS for camera access
- **Permission Denied** - Clear browser data and retry
- **Multiple Tabs** - Close other tabs using camera

### Performance Issues:
- **Low FPS** - Reduce image quality or resolution
- **High Latency** - Check network connection
- **Server Overload** - Monitor CPU/GPU usage

### Connection Problems:
- **Can't Connect** - Check firewall settings
- **Network Error** - Verify IP address and port
- **CORS Issues** - Run server with proper headers

## 🎪 Exhibition Use

Perfect for:
- **Tech Demos** - Live AI demonstrations
- **School Projects** - Interactive presentations  
- **Exhibitions** - Public AI showcases
- **Research** - Real-time emotion analysis
- **Social Events** - Fun interactive experiences

### Setup Tips:
1. **QR Code** - Generate QR code for easy mobile access
2. **Stable Network** - Use reliable WiFi connection
3. **Backup Plan** - Have offline demo ready
4. **Multiple Devices** - Test on various phones/tablets
5. **Clear Instructions** - Provide simple user guide

## 🚀 Performance Optimization

### Server Side:
- Use ONNX models for faster inference
- Implement frame skipping for better FPS
- Add caching for repeated detections
- Consider GPU acceleration

### Client Side:
- Reduce frame transmission rate
- Compress images before sending
- Implement client-side frame skipping
- Add loading states for better UX

---

🌟 **Ready to deploy publicly?** Check out the **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for production setup with custom domains and HTTPS!
