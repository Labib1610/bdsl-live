// Live sign inference: camera -> MediaPipe Tasks (VIDEO) -> normalize.js +
// pipeline.js -> ONNX Runtime Web. No build step, no framework. Serve the repo
// root with `python -m http.server` and open /app/web/index.html.
//
// Segmentation matches training/extraction: buffer raw frames while >=1 hand is
// present; when hands are absent for 5 consecutive frames and the segment has
// >=8 frames, run the full extract pipeline (dominant hand -> normalize +
// carry-forward -> left mirror -> resample to 48), compute first-diffs, and
// infer once. Uses window.{normalizeFrame,dominantLabel,buildFeatures,resample}.

import {
  HandLandmarker,
  PoseLandmarker,
  FilesetResolver,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14";

// ---- config (mirrors the Python pipeline) --------------------------------
const TASKS_VERSION = "0.10.14";
const ORT_VERSION = "1.19.2";
const WASM_ROOT = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${TASKS_VERSION}/wasm`;
const HAND_TASK =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";
const POSE_TASK =
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task";

const MODEL_URL = "../../models/model.onnx";
const VOCAB_URL = "../../data/vocabulary.json";

const N_FRAMES = 48; // resample target (src/extract_landmarks.py TARGET_FRAMES)
const COORD_DIM = 100; // normalize.js FEATURE_DIM
const INPUT_DIM = 200; // coords + first-diff
const ABSENT_LIMIT = 5; // consecutive hand-absent frames that end a segment
const MIN_SEGMENT = 8; // minimum buffered frames to bother inferring
const MAX_SEGMENT = 256; // safety cap so a continuous hand can't grow unbounded
const POSE_SUBSET = [0, 11, 12, 13, 14, 15, 16]; // nose, L/R shoulder, elbow, wrist

const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17],
];
// Indices into POSE_SUBSET: 0 nose,1 Lsh,2 Rsh,3 Lelb,4 Relb,5 Lwr,6 Rwr
const POSE_CONNECTIONS = [[1, 2], [1, 3], [3, 5], [2, 4], [4, 6]];

// ---- DOM -----------------------------------------------------------------
const els = {
  status: document.getElementById("status"),
  fallback: document.getElementById("fallback"),
  fallbackMsg: document.getElementById("fallback-msg"),
  fileInput: document.getElementById("fileInput"),
  video: document.getElementById("video"),
  overlay: document.getElementById("overlay"),
  fps: document.getElementById("fps"),
  recstate: document.getElementById("recstate"),
  reclabel: document.getElementById("reclabel"),
  preds: document.querySelectorAll("#preds .pred"),
  buffill: document.getElementById("buffill"),
  infcount: document.getElementById("infcount"),
};
const ctx = els.overlay.getContext("2d");

function setStatus(msg, isError = false) {
  els.status.textContent = msg;
  els.status.classList.toggle("error", isError);
}

// ---- state ---------------------------------------------------------------
let handLandmarker = null;
let poseLandmarker = null;
let session = null;
let idxToWord = [];

const rawBuffer = []; // { hands: {label: [[x,y]*21]}, pose: [[x,y]*7] | null }
let absentCount = 0;
let recording = false;
let segmentCount = 0;
let inferring = false;

let frameCount = 0;
let lastTs = 0;
let fpsEma = 0;
let lastFrameTime = performance.now();

// ---- init ----------------------------------------------------------------
async function initModels() {
  setStatus("loading vocabulary…");
  const vocab = await (await fetch(VOCAB_URL)).json();
  idxToWord = Object.entries(vocab).reduce((acc, [w, i]) => ((acc[i] = w), acc), []);

  setStatus("loading ONNX model…");
  ort.env.wasm.wasmPaths = `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/`;
  session = await ort.InferenceSession.create(MODEL_URL, { executionProviders: ["wasm"] });

  setStatus("loading MediaPipe models (first load downloads ~15 MB)…");
  const fileset = await FilesetResolver.forVisionTasks(WASM_ROOT);
  handLandmarker = await HandLandmarker.createFromOptions(fileset, {
    baseOptions: { modelAssetPath: HAND_TASK },
    runningMode: "VIDEO",
    numHands: 2,
  });
  poseLandmarker = await PoseLandmarker.createFromOptions(fileset, {
    baseOptions: { modelAssetPath: POSE_TASK },
    runningMode: "VIDEO",
    numPoses: 1,
  });
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false,
    });
    els.video.srcObject = stream;
    await els.video.play();
    setStatus("camera live — sign to the camera");
  } catch (err) {
    showFallback(`Camera unavailable (${err.name || err}). Load a video file instead.`);
    throw err;
  }
}

function showFallback(msg) {
  els.fallbackMsg.textContent = msg;
  els.fallback.classList.remove("hidden");
  setStatus(msg, true);
}

els.fileInput.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  els.video.srcObject = null;
  els.video.src = URL.createObjectURL(file);
  els.video.loop = true;
  await els.video.play();
  els.fallback.classList.add("hidden");
  setStatus(`playing file: ${file.name}`);
  syncCanvas();
});

function syncCanvas() {
  els.overlay.width = els.video.videoWidth || 640;
  els.overlay.height = els.video.videoHeight || 480;
}

// ---- per-frame extraction ------------------------------------------------
function toXY(landmarks) {
  return landmarks.map((p) => [p.x, p.y]);
}

function buildHandMap(handResult) {
  // {label -> [[x,y]*21]}, keeping the first hand for a duplicated label
  // (matches src/extract_landmarks.py::_detect_frame).
  const map = {};
  if (handResult && handResult.landmarks) {
    for (let i = 0; i < handResult.landmarks.length; i++) {
      const label = handResult.handedness[i][0].categoryName;
      if (!(label in map)) map[label] = toXY(handResult.landmarks[i]);
    }
  }
  return map;
}

function extractPose(poseResult) {
  if (poseResult && poseResult.landmarks && poseResult.landmarks.length) {
    const lm = poseResult.landmarks[0];
    return POSE_SUBSET.map((i) => [lm[i].x, lm[i].y]);
  }
  return null;
}

// ---- segment handling ----------------------------------------------------
function setRecording(on) {
  recording = on;
  els.recstate.classList.toggle("recording", on);
  els.recstate.classList.toggle("idle", !on);
  els.reclabel.textContent = on ? "recording" : "idle";
}

function resetSegment() {
  rawBuffer.length = 0;
  absentCount = 0;
  setRecording(false);
  els.buffill.textContent = 0;
}

function buildInputTensor(coords) {
  // coords: array of 48 Float32Array(100). -> (1,48,200) with first-diff,
  // matching src/dataset.py: [coords(100), diff(100)], diff[0]=0.
  const data = new Float32Array(N_FRAMES * INPUT_DIM);
  for (let t = 0; t < N_FRAMES; t++) {
    const cur = coords[t];
    const prev = t > 0 ? coords[t - 1] : null;
    const base = t * INPUT_DIM;
    for (let c = 0; c < COORD_DIM; c++) {
      data[base + c] = cur[c];
      data[base + COORD_DIM + c] = prev ? cur[c] - prev[c] : 0;
    }
  }
  return new ort.Tensor("float32", data, [1, N_FRAMES, INPUT_DIM]);
}

async function flushSegment() {
  const frames = rawBuffer.slice();
  resetSegment();
  if (frames.length < MIN_SEGMENT || inferring) return;

  inferring = true;
  try {
    const handMaps = frames.map((f) => f.hands);
    const poses = frames.map((f) => f.pose);
    const dominant = dominantLabel(handMaps);
    const arr = buildFeatures(handMaps, poses, dominant); // (T,100)
    const resampled = resample(arr, N_FRAMES); // (48,100)
    const out = await session.run({ features: buildInputTensor(resampled) });
    renderTop3(softmaxTop3(out.logits.data));
    segmentCount++;
    els.infcount.textContent = segmentCount;
  } finally {
    inferring = false;
  }
}

function softmaxTop3(logits) {
  let max = -Infinity;
  for (const v of logits) if (v > max) max = v;
  let sum = 0;
  const exps = new Float32Array(logits.length);
  for (let i = 0; i < logits.length; i++) {
    exps[i] = Math.exp(logits[i] - max);
    sum += exps[i];
  }
  const idx = Array.from(logits.keys()).sort((a, b) => logits[b] - logits[a]).slice(0, 3);
  return idx.map((i) => ({ word: idxToWord[i], conf: exps[i] / sum }));
}

function renderTop3(top3) {
  top3.forEach((p, i) => {
    const el = els.preds[i];
    el.querySelector(".label").textContent = p.word;
    el.querySelector(".conf").textContent = `${(p.conf * 100).toFixed(1)}%`;
    el.style.setProperty("--bar", `${(p.conf * 100).toFixed(1)}%`);
  });
}

// ---- overlay drawing -----------------------------------------------------
function drawEdges(pts, connections, color, w, h) {
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  for (const [a, b] of connections) {
    ctx.beginPath();
    ctx.moveTo(pts[a][0] * w, pts[a][1] * h);
    ctx.lineTo(pts[b][0] * w, pts[b][1] * h);
    ctx.stroke();
  }
  for (const p of pts) {
    ctx.beginPath();
    ctx.arc(p[0] * w, p[1] * h, 3, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawOverlay(handResult, poseResult) {
  const w = els.overlay.width;
  const h = els.overlay.height;
  ctx.clearRect(0, 0, w, h);
  if (poseResult && poseResult.landmarks && poseResult.landmarks.length) {
    const lm = poseResult.landmarks[0];
    drawEdges(POSE_SUBSET.map((i) => [lm[i].x, lm[i].y]), POSE_CONNECTIONS, "#4ab3ff", w, h);
  }
  if (handResult && handResult.landmarks) {
    for (let i = 0; i < handResult.landmarks.length; i++) {
      const label = handResult.handedness[i][0].categoryName;
      drawEdges(toXY(handResult.landmarks[i]), HAND_CONNECTIONS,
        label === "Right" ? "#4cc38a" : "#ffa64c", w, h);
    }
  }
}

// ---- main loop -----------------------------------------------------------
function loop() {
  if (els.video.readyState >= 2 && handLandmarker && poseLandmarker) {
    if (!els.overlay.width || !els.overlay.height) syncCanvas();

    let ts = performance.now();
    if (ts <= lastTs) ts = lastTs + 1; // strictly increasing for VIDEO mode
    lastTs = ts;

    const handResult = handLandmarker.detectForVideo(els.video, ts);
    const poseResult = poseLandmarker.detectForVideo(els.video, ts);
    drawOverlay(handResult, poseResult);

    const hands = buildHandMap(handResult);
    if (Object.keys(hands).length >= 1) {
      rawBuffer.push({ hands, pose: extractPose(poseResult) });
      absentCount = 0;
      if (!recording) setRecording(true);
      if (rawBuffer.length >= MAX_SEGMENT) flushSegment();
    } else {
      absentCount++;
      if (recording && absentCount >= ABSENT_LIMIT) {
        // >=5 absent frames end the segment: infer if long enough, else discard.
        if (rawBuffer.length >= MIN_SEGMENT) flushSegment();
        else resetSegment();
      }
    }
    els.buffill.textContent = rawBuffer.length;

    frameCount++;
    const now = performance.now();
    const instFps = 1000 / Math.max(1, now - lastFrameTime);
    lastFrameTime = now;
    fpsEma = fpsEma ? fpsEma * 0.9 + instFps * 0.1 : instFps;
    els.fps.textContent = `${fpsEma.toFixed(1)} fps`;
  }
  requestAnimationFrame(loop);
}

// ---- boot ----------------------------------------------------------------
(async function main() {
  try {
    await initModels();
  } catch (err) {
    showFallback(`Model init failed: ${err.message || err}`);
    return;
  }
  try {
    await startCamera();
  } catch {
    // fallback UI already shown; the loop still runs once a file is loaded
  }
  els.video.addEventListener("loadedmetadata", syncCanvas);
  syncCanvas();
  requestAnimationFrame(loop);
})();
