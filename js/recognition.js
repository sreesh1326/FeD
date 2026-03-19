/* ═══════════════════════════════════════════════════════
   FeD — recognition.js
   Recognition Module: model loading, face matching, canvas drawing
   ═══════════════════════════════════════════════════════ */

const Recognition = (() => {

  const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api@1.7.2/model';

  /* status: 'loading' | 'ready' | 'sim' */
  let _status = 'loading';

  /* cooldown: prevent spamming the same attendance */
  let _lastMarkedRoll = null;
  let _lastMarkedAt   = 0;
  const COOLDOWN_MS   = 6000;

  /* ── Model loading ──────────────────────────────────── */
  async function loadModels() {
    const dot    = document.getElementById('loaderDot');
    const text   = document.getElementById('loaderText');
    const fill   = document.getElementById('loaderFill');

    const step = (pct, msg) => {
      if (fill) fill.style.width = pct + '%';
      if (text) text.textContent = msg;
    };

    try {
      step(10, 'Loading TinyFaceDetector…');
      await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);

      step(50, 'Loading FaceLandmark68Net…');
      await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);

      step(85, 'Loading FaceRecognitionNet…');
      await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);

      step(100, 'All models loaded — system ready');
      if (dot) { dot.className = 'loader-dot ready'; }
      _status = 'ready';
      UI.setStatus('online', 'ONLINE');
      UI.toast('Face recognition engine ready.', 'success');

    } catch (err) {
      console.warn('[Recognition] Model load failed, entering simulation mode:', err);
      if (dot)  dot.className = 'loader-dot error';
      if (text) text.textContent = 'Simulation mode — models unavailable';
      _status = 'sim';
      UI.setStatus('sim', 'SIMULATION');
      UI.toast('Simulation mode active (CDN models unavailable).', 'warning');
    }
  }

  function modelsReady() { return _status === 'ready'; }

  /* ── Build FaceMatcher from registered descriptors ─── */
  function buildMatcher() {
    const students = App.getStudents();
    const labeled  = students
      .filter(s => s.descriptor && s.descriptor.length > 0)
      .map(s => new faceapi.LabeledFaceDescriptors(
        s.roll,
        [new Float32Array(s.descriptor)]
      ));
    if (labeled.length === 0) return null;
    return new faceapi.FaceMatcher(labeled, 0.52);
  }

  /* ── Extract descriptor from a captured image ──────── */
  async function extractDescriptor(imageDataUrl) {
    if (_status !== 'ready') return null;
    try {
      // Create an img element to feed to face-api
      const img = await new Promise((resolve, reject) => {
        const el = new Image();
        el.onload  = () => resolve(el);
        el.onerror = reject;
        el.src     = imageDataUrl;
      });
      const det = await faceapi
        .detectSingleFace(img, new faceapi.TinyFaceDetectorOptions({ scoreThreshold: 0.4 }))
        .withFaceLandmarks()
        .withFaceDescriptor();
      return det ? Array.from(det.descriptor) : null;
    } catch (err) {
      console.error('[Recognition] extractDescriptor:', err);
      return null;
    }
  }

  /* ── Attendance recognition loop (called per frame) ── */
  async function runDetection(video, canvas, ctx) {
    if (_status === 'ready') {
      await _realDetection(video, ctx);
    } else if (_status === 'sim') {
      _simulateDetection(canvas, ctx);
    }
  }

  async function _realDetection(video, ctx) {
    const W = video.videoWidth, H = video.videoHeight;
    const scaleX = (ctx.canvas.width  / W) || 1;
    const scaleY = (ctx.canvas.height / H) || 1;

    let detections;
    try {
      detections = await faceapi
        .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions({ scoreThreshold: 0.4 }))
        .withFaceLandmarks()
        .withFaceDescriptors();
    } catch (_) { return; }

    const matcher = buildMatcher();

    for (const det of detections) {
      const { x, y, width, height } = det.detection.box;
      const bx = x * scaleX, by = y * scaleY;
      const bw = width * scaleX, bh = height * scaleY;

      let student = null;
      if (matcher) {
        const match = matcher.findBestMatch(det.descriptor);
        if (match.label !== 'unknown') {
          student = App.getStudents().find(s => s.roll === match.label) || null;
        }
      }

      _drawBox(ctx, bx, by, bw, bh, student ? student.name : 'Unknown', !!student);

      if (student) _tryMarkattendance(student);
    }
  }

  let _simFrame = 0;
  function _simulateDetection(canvas, ctx) {
    _simFrame++;
    if (_simFrame % 2 !== 0) return; // slow down sim rate

    const students = App.getStudents();
    if (students.length === 0) return;

    const W = canvas.width, H = canvas.height;
    const bw = 160, bh = 200;
    const bx = (W - bw) / 2, by = (H - bh) / 2;

    const student = students[0];
    _drawBox(ctx, bx, by, bw, bh, student.name, true);

    if (Date.now() - _lastMarkedAt > COOLDOWN_MS) {
      _tryMarkAttendance(student);
    }
  }

  /* ── Drawing helpers ────────────────────────────────── */
  function _drawBox(ctx, x, y, w, h, label, matched) {
    const color = matched ? '#34d399' : '#f87171';
    const labelH = 24;

    // Bounding box
    ctx.strokeStyle = color;
    ctx.lineWidth   = 2;
    ctx.strokeRect(x, y, w, h);

    // Corner accents
    const cs = 14;
    ctx.strokeStyle = color;
    ctx.lineWidth   = 3;
    [[x,y],[x+w,y],[x,y+h],[x+w,y+h]].forEach(([cx,cy], i) => {
      ctx.beginPath();
      ctx.moveTo(cx + (i%2===0 ? cs : -cs), cy);
      ctx.lineTo(cx, cy);
      ctx.lineTo(cx, cy + (i<2 ? cs : -cs));
      ctx.stroke();
    });

    // Label background
    ctx.fillStyle = matched ? 'rgba(52,211,153,0.88)' : 'rgba(248,113,113,0.88)';
    ctx.fillRect(x, y - labelH, w, labelH);

    // Label text
    ctx.fillStyle = '#fff';
    ctx.font      = 'bold 12px "Syne", sans-serif';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x + 6, y - labelH / 2);
  }

  /* ── Attendance marker ──────────────────────────────── */
  function _tryMarkAttendance(student) {
    const now = Date.now();
    if (student.roll === _lastMarkedRoll && now - _lastMarkedAt < COOLDOWN_MS) return;
    _lastMarkedRoll = student.roll;
    _lastMarkedAt   = now;
    App.markAttendance(student);
    setTimeout(() => Camera.stopAttendanceCamera(), 800);
  }

  /* ── Public API ─────────────────────────────────────── */
  return { loadModels, modelsReady, extractDescriptor, runDetection };

})();
