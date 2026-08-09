# Spec 04 — Browser inference app

## Goal
Static web app: camera → MediaPipe Tasks (JS) → normalize → ONNX Runtime Web
→ live top-3 predictions. Plus an automated parity test vs the Python pipeline.

## Part A — parity fixture (do this FIRST)
1. `scripts/make_parity_fixture.py` — pick 3 trials, save to
   `app/web/fixtures/{trial_id}.json`: raw MediaPipe hand+pose landmark arrays
   per frame (pre-normalization), plus the expected (48,100) normalized output
   from `src/normalize.py`.
2. `app/web/normalize.js` — verbatim port of `src/normalize.py`. Same order of
   operations, same constants. No refactoring, no "improvements".
3. `app/web/parity.test.js` — loads fixtures, runs normalize.js, asserts
   max abs diff < 1e-5 vs the Python expected output.
   **This test must pass before any UI work.**

## Part B — app
- `index.html`, `app.js`, `style.css`. No build step, no framework.
- MediaPipe Tasks Vision from CDN: HandLandmarker + PoseLandmarker, VIDEO mode.
- ONNX Runtime Web from CDN, wasm backend. Load `models/model.onnx`.
- Rolling 48-frame buffer of normalized frames. Compute first-diffs in JS →
  (1, 48, 200) tensor, matching the Python loader exactly.
- Run inference every 5 frames on the current buffer.
- Display: live video with landmark overlay, top-3 predictions with confidence,
  current FPS.
- Camera denied / unavailable → clear message + a "load a video file" fallback.

## Part C — sanity check
`scripts/browser_sanity.md` — manual checklist:
- open app, allow camera, confirm landmarks track hands
- confirm FPS >= 15 (log actual)
- confirm predictions change when you move vs stay still

## Constraints
- Plain JS, no bundler. Must work when served by `python -m http.server`.
- `normalize.js` has NO dependencies.
- Do not modify `src/normalize.py`.

## Acceptance
- parity test passes at < 1e-5
- app loads and runs inference in Chrome
- FPS logged