# Browser inference — manual sanity checklist (Spec 04, Part C)

The parity test and static serving are automated; the live camera/inference path
needs a human with a webcam in Chrome. Work through this list and fill in the
`actual` fields.

## 0. Prerequisites (automated — should already pass)
- [ ] `node app/web/parity.test.js` prints `PARITY OK` (max abs diff < 1e-5).
- [ ] `models/model.onnx` exists (run `python src/export_onnx.py` if not).

## 1. Serve + open
Serve from the **repo root** so `../../models/` and `../../data/` resolve:

```bash
cd <repo root>
python -m http.server 8000
```

Open **http://localhost:8000/app/web/index.html** in Chrome.

- [ ] Page loads; status shows model/MediaPipe loading, then "camera live…".
      (First load downloads ~15 MB of MediaPipe wasm+models — allow a few seconds.)

## 2. Camera + landmark tracking
- [ ] Browser prompts for camera permission; click **Allow**.
- [ ] Live video appears (mirrored, selfie-style).
- [ ] Green (hand A / right) and orange (hand B / left) skeletons track your
      hands; blue pose skeleton tracks shoulders/elbows/wrists.
- [ ] `buffer: N/48` climbs to 48 within ~2 seconds.

## 3. FPS  (>= 15 required)
- [ ] Top-left overlay shows a live FPS readout.
- [ ] FPS is **>= 15**.

> actual FPS observed: `____`  (machine / Chrome version: `____`)

## 4. Predictions respond to motion
- [ ] With the buffer full, the Top-3 panel shows word ids (e.g. `W11`) with
      confidences and a green bar.
- [ ] **Stay still** for ~2 s → predictions/confidences settle and barely change.
- [ ] **Sign / move your hands** → the Top-3 list and confidences visibly change.
- [ ] `inferences:` counter increases (~1 per 5 frames).

## 5. Camera-denied fallback
- [ ] Reload, click **Block** on the camera prompt (or run with no webcam).
- [ ] A clear error message appears with a **"load a video file"** button.
- [ ] Choosing a local video file starts playback and inference runs on it.

## Notes / known limitations
- Hand A is assigned to the **Right**-labelled hand (right-dominant canonical, as
  in training). Left-dominant signing is not mirrored live, so expect weaker
  predictions for left-dominant users — a known demo limitation.
- MediaPipe handedness is reported from the image's perspective; with a mirrored
  selfie feed the Left/Right labels may feel flipped. Predictions still work
  because the same convention was used to build the canonical training data.
