# FeD — Face Detection Attendance System

> A browser-based face recognition attendance system built with vanilla HTML, CSS, and JavaScript using the `face-api.js` library.

---

## 📁 Project Structure

```
FeD/
├── index.html          ← Main HTML entry point
├── css/
│   └── style.css       ← All styles (purple & black theme)
├── js/
│   ├── ui.js           ← UI utilities: tabs, toast, clock, helpers
│   ├── camera.js       ← Webcam control (registration & attendance)
│   ├── recognition.js  ← Face-api model loading, detection, matching
│   └── app.js          ← State management, registration, attendance logic
└── README.md
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Student Registration** | Name, Roll Number, Department + live face capture |
| **Face Recognition** | Real-time detection using TinyFaceDetector + FaceRecognitionNet |
| **IST Timestamps** | All records stamped in Indian Standard Time (UTC+5:30) |
| **Attendance Log** | Full table with serial number, name, roll, dept, date-time |
| **Persistence** | Data stored in `localStorage` (survives page refresh) |
| **Simulation Mode** | Fallback UI when CDN models are unavailable |
| **Responsive UI** | Works on desktop and mobile browsers |

---

## 🚀 Getting Started

### Option 1 — Open directly (simplest)
Just open `index.html` in **Google Chrome** or **Microsoft Edge**.

> ⚠️ Due to browser security policies (CORS), the face-api models load from the jsDelivr CDN. An internet connection is required for full face recognition.

### Option 2 — Serve with a local server (recommended for best results)

```bash
# Using Python
python -m http.server 8080

# Using Node.js (npx)
npx serve .
```

Then open `http://localhost:8080` in your browser.

---

## 🧭 How to Use

### Step 1 — Register Students
1. Go to the **Register** tab
2. Fill in: Full Name, Roll Number, Department
3. Click **Open Camera** → position face in frame
4. Click **Capture Face** when the green *"Face Detected"* badge appears
5. Click **Register Student**

### Step 2 — Mark Attendance
1. Go to the **Attendance** tab
2. Click **Start Camera**
3. The system scans in real time — recognized students get a **green box** and their attendance is logged automatically
4. Unknown faces receive a **red box**

### Step 3 — View Records
1. Go to the **Records** tab
2. View stats: total records, today's count, registered students
3. Full table with IST timestamps for every entry

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Structure | Semantic HTML5 |
| Styling | Pure CSS3 (custom properties, CSS Grid, Flexbox) |
| Logic | Vanilla JavaScript (ES6+ modules via IIFE pattern) |
| Face Detection | [face-api.js](https://github.com/vladmandic/face-api) (TinyFaceDetector + FaceLandmark68 + FaceRecognition) |
| Storage | Browser `localStorage` |
| Fonts | Syne (display) + JetBrains Mono (monospace) via Google Fonts |

---

## 📦 JavaScript Module Overview

### `js/ui.js` — UI Module
- `UI.getIST()` — returns current Indian Standard Time `Date` object
- `UI.formatIST(iso)` — formats an ISO string to a readable IST string
- `UI.startClock()` — starts the live clock in the header
- `UI.switchTab(id)` — switches the active panel/tab
- `UI.toast(msg, type)` — shows a floating notification (`info|success|error|warning`)
- `UI.setStatus(state, label)` — updates the system status badge
- `UI.initials(name)` — returns 2-letter initials for avatar display

### `js/camera.js` — Camera Module
- `Camera.startRegCamera()` — opens webcam for registration
- `Camera.stopRegCamera()` — closes registration webcam
- `Camera.captureForReg()` — captures a frame and passes to App
- `Camera.startAttendanceCamera()` — opens webcam for live recognition loop
- `Camera.stopAttendanceCamera()` — stops attendance recognition

### `js/recognition.js` — Recognition Module
- `Recognition.loadModels()` — downloads face-api neural network models
- `Recognition.modelsReady()` — returns `true` if models loaded successfully
- `Recognition.extractDescriptor(dataUrl)` — extracts 128-D face embedding from image
- `Recognition.runDetection(video, canvas, ctx)` — detects + matches faces, draws boxes

### `js/app.js` — App Module (State & Logic)
- `App.init()` — bootstraps the entire application
- `App.registerStudent()` — validates form, extracts descriptor, saves student
- `App.deleteStudent(roll)` — removes a student by roll number
- `App.markAttendance(student)` — creates an IST-stamped attendance record
- `App.updateRecords()` — re-renders the attendance log table
- `App.clearRecords()` — clears all attendance history

---

## 🌐 Browser Compatibility

| Browser | Status |
|---|---|
| Chrome 90+ | ✅ Full support |
| Edge 90+ | ✅ Full support |
| Firefox 90+ | ✅ Full support |
| Safari 15+ | ⚠️ Camera may require HTTPS |

---

## 🔒 Privacy Note

All face data (embeddings) is stored **locally in your browser** via `localStorage`. No data is sent to any external server. Face images are stored only temporarily during registration.

---

## 👨‍💻 Author

Built for **FeD — Face Detection Attendance System**  
Showcases real-time computer vision in the browser using modern JavaScript.

---

*Designed with a professional purple & black UI theme for portfolio use.*
