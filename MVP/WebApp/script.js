// Modern Person Tracker - Optimized JavaScript
class PersonTracker {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.isProcessing = false;
        this.animationId = null;
        
        // AI Processing state
        this.isAIProcessing = false;
        this.lastProcessedFrame = null;
        this.maxConcurrentRequests = 1;
        this.activeRequests = 0;
        
        // UI elements
        this.startBtn = document.getElementById('startButton');
        this.stopBtn = document.getElementById('stopButton');
        this.statusText = document.getElementById('statusText');
        this.statusSpan = document.getElementById('status');
        this.fpsSpan = document.getElementById('fps');
        this.personsSpan = document.getElementById('persons');
        this.loading = document.getElementById('loading');        // Performance tracking        this.displayFrameCount = 0;
        this.lastDisplayTime = performance.now();
        this.lastAIProcessTime = 0;
        // Removed aiProcessingInterval - let machine process as fast as possible
        this.serverFPS = 0; // Track server-side FPS

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.startBtn.addEventListener('click', () => this.startCamera());
        this.stopBtn.addEventListener('click', () => this.stopCamera());
        
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isProcessing) {
                console.log('Tab hidden, continuing processing...');
            }
        });

        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleResize(), 500);
        });

        // Handle resize
        window.addEventListener('resize', () => this.handleResize());
    }

    handleResize() {
        if (this.isProcessing && this.video.videoWidth && this.video.videoHeight) {
            this.setCanvasDimensions();
        }
    }

    setCanvasDimensions() {
        // Set canvas dimensions to match video aspect ratio
        const aspectRatio = this.video.videoWidth / this.video.videoHeight;
        const containerWidth = this.canvas.parentElement.clientWidth;
        const containerHeight = this.canvas.parentElement.clientHeight;
        
        let canvasWidth, canvasHeight;
        
        if (containerWidth / containerHeight > aspectRatio) {
            canvasHeight = containerHeight;
            canvasWidth = containerHeight * aspectRatio;
        } else {
            canvasWidth = containerWidth;
            canvasHeight = containerWidth / aspectRatio;
        }
        
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        this.canvas.style.width = `${canvasWidth}px`;
        this.canvas.style.height = `${canvasHeight}px`;
    }

    async startCamera() {
        try {
            this.showLoading(true);
            this.updateStatus('Requesting camera access...', 'Starting');
            
            // Request camera with optimized settings for performance
            const constraints = {
                video: {
                    facingMode: 'user',
                    width: { ideal: 640, max: 1280 }, // Reduced resolution for better performance
                    height: { ideal: 480, max: 720 },
                    frameRate: { ideal: 30, max: 30 }
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            // Wait for video metadata to load
            await this.waitForVideoReady();
            
            this.video.play();
            this.setCanvasDimensions();
            
            this.showLoading(false);
            this.isProcessing = true;
            this.updateStatus('AI detection active', 'Active');
            
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
              // Reset performance counters
            this.displayFrameCount = 0;
            this.lastDisplayTime = performance.now();
            this.lastAIProcessTime = 0;
            this.serverFPS = 0;
            
            // Start the optimized processing loops
            this.startVideoLoop();
            this.startAILoop();
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.handleCameraError(error);
        }
    }

    waitForVideoReady() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video loading timeout'));
            }, 10000);

            this.video.onloadedmetadata = () => {
                clearTimeout(timeout);
                resolve();
            };

            this.video.onerror = () => {
                clearTimeout(timeout);
                reject(new Error('Video loading failed'));
            };
        });
    }

    handleCameraError(error) {
        this.showLoading(false);
        
        let errorMessage = 'Camera access failed';
        let statusMessage = 'Error';
        
        if (error.name === 'NotAllowedError') {
            errorMessage = 'Camera permission denied. Please allow camera access and try again.';
        } else if (error.name === 'NotFoundError') {
            errorMessage = 'No camera found. Please connect a camera and try again.';
        } else if (error.name === 'NotReadableError') {
            errorMessage = 'Camera is being used by another application.';
        } else if (error.name === 'OverconstrainedError') {
            errorMessage = 'Camera settings not supported. Trying with basic settings...';
            this.startCameraBasic();
            return;
        }
        
        this.updateStatus(errorMessage, statusMessage);
        this.showErrorAlert(errorMessage);
    }

    async startCameraBasic() {
        try {
            const basicConstraints = {
                video: {
                    facingMode: 'user',
                    width: { ideal: 480, max: 640 }, // Even lower resolution for compatibility
                    height: { ideal: 360, max: 480 }
                }
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(basicConstraints);
            this.video.srcObject = this.stream;
            await this.waitForVideoReady();
            this.video.play();
            this.setCanvasDimensions();
            
            this.showLoading(false);
            this.isProcessing = true;
            this.updateStatus('AI detection active (basic mode)', 'Active');
            
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            
            this.startVideoLoop();
            this.startAILoop();
            
        } catch (error) {
            this.handleCameraError(error);
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => {
                track.stop();
                console.log(`Stopped ${track.kind} track`);
            });
            this.stream = null;
        }
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
          this.isProcessing = false;
        this.activeRequests = 0;
        this.serverFPS = 0; // Reset server FPS
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.updateStatus('Detection stopped', 'Stopped');
        this.updateStats(0, 0);
        
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
    }

    // Separate high-frequency video display loop
    startVideoLoop() {
        const videoLoop = () => {
            if (!this.isProcessing) return;

            // Always show live video for smooth display
            if (this.lastProcessedFrame) {
                // Show processed frame with detections
                this.displayProcessedFrame(this.lastProcessedFrame);
            } else {
                // Show live video while waiting for AI processing
                this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            }
            
            // Calculate and update display FPS
            this.updateFPS();

            // Continue the video loop at high frequency (60fps)
            this.animationId = requestAnimationFrame(videoLoop);
        };
        
        videoLoop();
    }    // Separate low-frequency AI processing loop
    startAILoop() {
        const aiLoop = async () => {
            if (!this.isProcessing) return;

            // Process AI immediately if not already processing
            if (this.activeRequests < this.maxConcurrentRequests) {
                this.processFrameWithAI();
            }

            // Continue AI loop as fast as possible
            requestAnimationFrame(aiLoop);
        };
        
        aiLoop();
    }

    async processFrameWithAI() {
        if (this.activeRequests >= this.maxConcurrentRequests) return;

        this.activeRequests++;

        try {
            // Create smaller canvas for AI processing to improve performance
            const aiCanvas = document.createElement('canvas');
            const maxDimension = 416; // Smaller size for faster processing
            const scale = Math.min(maxDimension / this.video.videoWidth, maxDimension / this.video.videoHeight);
            
            aiCanvas.width = Math.floor(this.video.videoWidth * scale);
            aiCanvas.height = Math.floor(this.video.videoHeight * scale);
            
            const aiCtx = aiCanvas.getContext('2d');
            aiCtx.drawImage(this.video, 0, 0, aiCanvas.width, aiCanvas.height);
            
            // Convert to base64 with lower quality for faster transfer
            const imageData = aiCanvas.toDataURL('image/jpeg', 0.5);

            // Send frame to server for processing (non-blocking)
            const response = await fetch('/process_frame', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                },
                body: JSON.stringify({ image: imageData })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
              if (result.success) {
                // Store the latest processed frame
                this.lastProcessedFrame = result.processed_image;
                
                // Update server FPS
                if (result.fps !== undefined) {
                    this.serverFPS = result.fps;
                }
                
                // Update stats
                if (result.total_persons !== undefined) {
                    this.personsSpan.textContent = result.total_persons;
                }
                
                // Update status based on detection
                if (result.total_persons > 0) {
                    this.statusSpan.textContent = 'Detecting';
                } else {
                    this.statusSpan.textContent = 'Active';
                }
                
            } else {
                console.error('Processing error:', result.error);
                this.updateStatus('Processing error occurred', 'Error');
            }
            
        } catch (error) {
            console.error('Error processing frame:', error);
            
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                this.updateStatus('Connection error - check server', 'Offline');
            } else {
                this.updateStatus('Processing error', 'Error');
            }
        } finally {
            this.activeRequests--;
        }
    }

    displayProcessedFrame(processedImageData) {
        if (!this.processedImage || this.processedImage.src !== processedImageData) {
            this.processedImage = new Image();
            this.processedImage.onload = () => {
                if (this.isProcessing) {
                    this.ctx.drawImage(this.processedImage, 0, 0, this.canvas.width, this.canvas.height);
                }
            };
            this.processedImage.src = processedImageData;
        } else {
            // Use cached image for better performance
            this.ctx.drawImage(this.processedImage, 0, 0, this.canvas.width, this.canvas.height);
        }
    }    updateFPS() {
        // Display server-side FPS instead of client-side display FPS
        if (this.serverFPS > 0) {
            this.fpsSpan.textContent = this.serverFPS.toFixed(1);
        }
    }

    showLoading(show) {
        this.loading.style.display = show ? 'flex' : 'none';
    }

    updateStatus(message, status) {
        this.statusText.textContent = message;
        if (status) {
            this.statusSpan.textContent = status;
        }
    }    updateStats(fps, persons) {
        if (fps !== undefined) {
            this.serverFPS = fps;
            this.fpsSpan.textContent = fps.toFixed(1);
        }
        if (persons !== undefined) {
            this.personsSpan.textContent = persons;
        }
    }

    showErrorAlert(message) {
        // Create a custom alert that matches the design
        const alertOverlay = document.createElement('div');
        alertOverlay.className = 'error-overlay';
        alertOverlay.innerHTML = `
            <div class="error-dialog glass-card">
                <div class="error-icon">⚠️</div>
                <h3>Camera Error</h3>
                <p>${message}</p>
                <button class="btn btn-primary error-btn">OK</button>
            </div>
        `;
        
        document.body.appendChild(alertOverlay);
        
        const okBtn = alertOverlay.querySelector('.error-btn');
        okBtn.addEventListener('click', () => {
            document.body.removeChild(alertOverlay);
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(alertOverlay)) {
                document.body.removeChild(alertOverlay);
            }
        }, 5000);
    }

    // Method to check if device has camera
    static async checkCameraAvailability() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.some(device => device.kind === 'videoinput');
        } catch (error) {
            console.error('Error checking camera availability:', error);
            return false;
        }
    }

    // Method to get camera info
    static async getCameraInfo() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(device => device.kind === 'videoinput');
            return cameras.map(camera => ({
                id: camera.deviceId,
                label: camera.label || 'Unknown Camera'
            }));
        } catch (error) {
            console.error('Error getting camera info:', error);
            return [];
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    // Check if camera is available
    const hasCameras = await PersonTracker.checkCameraAvailability();
    
    if (!hasCameras) {
        console.warn('No cameras detected');
        const statusText = document.getElementById('statusText');
        statusText.textContent = 'No camera detected. Please connect a camera and refresh the page.';
        
        const startBtn = document.getElementById('startButton');
        startBtn.disabled = true;
        startBtn.innerHTML = '<span class="btn-icon">📷</span><span>No Camera</span>';
    }
    
    // Initialize the person tracker
    const tracker = new PersonTracker();
    
    // Add some visual feedback
    console.log('🤖 AI Person Tracker initialized');
    console.log('📱 Optimized for high performance!');
});

// Add error overlay styles dynamically
const errorStyles = `
    .error-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        backdrop-filter: blur(10px);
        animation: fadeIn 0.3s ease;
    }

    .error-dialog {
        max-width: 320px;
        padding: 32px;
        text-align: center;
        margin: 20px;
        animation: slideUp 0.3s ease;
    }

    .error-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }

    .error-dialog h3 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--text-primary);
    }

    .error-dialog p {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.5;
        margin-bottom: 24px;
    }

    .error-btn {
        width: 100%;
        margin: 0;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateY(20px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = errorStyles;
document.head.appendChild(styleSheet);
