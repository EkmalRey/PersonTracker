# Minimum Viable Product (MVP)

This MVP consists of a `.py` file that runs inference for **person detection and tracking** using **YOLO**.  
It comes with a few features such as:

- Person detection using YOLO with ByteTrack tracking.
- Realtime face detection inside detected person bounding boxes using Haar Cascade Classifier.
- Track history visualization with polylines.
- Source input from YouTube livestream or local webcam.
- FPS counter and total person count overlay.
- Automatically fetches stream URL from YouTube using `yt-dlp`.

---

## Usage:

```bash
python DetectAndTrack.py --source [youtube|webcam] --youtube_url [YouTube Link] --webcam_id [Device ID] --model [YOLO Model] --conf [Confidence Threshold]
```

### Example:
```bash
python DetectAndTrack.py --source youtube --youtube_url "https://youtu.be/dQw4w9WgXcQ?si=bc6ATN4F77QG9ZQt" --model yolov8n.pt --conf 0.4
```
or
```bash
python your_script.py --source webcam --webcam_id 0 --model yolov8n.pt --conf 0.4
```

---

## Requirements:

- Python 3.8+
- `ultralytics`  
- `opencv-python`  
- `numpy`  
- `yt-dlp`
- `fer`

Install them via:

```bash
pip install -r requirements.txt
```

---

## TODO:
- Add Re-Identification so ID number wouldnt go sky high
- Add GUI at the start
- Add GUI for control (change source while running, pause, start, fps control)
- Refactor Code

---
✅ **Note:** Make sure `yt-dlp` is installed and accessible from your system path if you plan to stream from YouTube.  
You can also test your YOLO model by adjusting the `--model` argument to your own `.pt` file.
