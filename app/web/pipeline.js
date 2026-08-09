// Ports of the trial-processing steps from src/extract_landmarks.py:
//   _dominant_label  -> dominantLabel
//   _build_features  -> buildFeatures   (normalize + carry-forward + left mirror)
//   _resample        -> resample        (linear interp of the time axis to 48)
//
// Kept separate from normalize.js (which is a verbatim port of normalize.py) so
// that file stays pristine. Depends only on normalizeFrame. Works in Node
// (require) and the browser (window globals). Match Python EXACTLY — no
// "improvements".

(function () {
  const normalizeFrame =
    typeof require !== "undefined" && typeof module !== "undefined"
      ? require("./normalize.js").normalizeFrame
      : (typeof window !== "undefined" ? window : globalThis).normalizeFrame;

  const FEATURE_DIM = 100;
  const HAND_BLOCK = 42; // hand A: [0,42), hand B: [42,84)
  const WRIST_LM = 0;

  // src/extract_landmarks.py::_dominant_label
  function dominantLabel(handMaps) {
    const singles = [];
    for (const m of handMaps) {
      const keys = Object.keys(m);
      if (keys.length === 1) singles.push(keys[0]);
    }
    if (singles.length) {
      const left = singles.filter((s) => s === "Left").length;
      const right = singles.filter((s) => s === "Right").length;
      if (left === right) return "Right"; // deterministic tie-break toward canonical
      return left > right ? "Left" : "Right";
    }

    // No single-hand frame anywhere: fall back to wrist displacement.
    const disp = { Left: 0.0, Right: 0.0 };
    const prev = {};
    for (const m of handMaps) {
      for (const label of Object.keys(m)) {
        const wrist = m[label][WRIST_LM];
        if (label in prev) {
          const dx = wrist[0] - prev[label][0];
          const dy = wrist[1] - prev[label][1];
          disp[label] += Math.sqrt(dx * dx + dy * dy);
        }
        prev[label] = wrist;
      }
    }
    if (disp.Left === disp.Right) return "Right";
    return disp.Left > disp.Right ? "Left" : "Right";
  }

  // src/extract_landmarks.py::_build_features -> array of Float32Array(100)
  function buildFeatures(handMaps, poses, dominant) {
    const other = dominant === "Left" ? "Right" : "Left";

    const arr = [];
    let lastValid = null;
    for (let t = 0; t < handMaps.length; t++) {
      const hm = handMaps[t] || {};
      const slots = [
        hm[dominant] !== undefined ? hm[dominant] : null,
        hm[other] !== undefined ? hm[other] : null,
      ];
      let vec = normalizeFrame(slots, poses[t] !== undefined ? poses[t] : null);
      if (!Number.isFinite(vec[0])) {
        // invalid frame -> carry forward previous valid (or zeros if none yet)
        vec = lastValid !== null ? lastValid.slice() : new Float32Array(FEATURE_DIM);
      } else {
        lastValid = vec;
      }
      arr.push(vec);
    }

    if (dominant === "Left") {
      // Mirror to right-dominant canonical: negate every x coord, then swap the
      // two hand blocks (and their presence flags). Order matches Python.
      for (const vec of arr) {
        for (let i = 0; i < 98; i += 2) vec[i] = -vec[i];
        for (let k = 0; k < HAND_BLOCK; k++) {
          const tmp = vec[k];
          vec[k] = vec[HAND_BLOCK + k];
          vec[HAND_BLOCK + k] = tmp;
        }
        const fa = vec[98];
        vec[98] = vec[99];
        vec[99] = fa;
      }
    }

    return arr;
  }

  // src/extract_landmarks.py::_resample  (numpy.interp over np.linspace(0, T-1, n))
  function resample(arr, n) {
    const T = arr.length;
    const D = arr[0].length;
    const step = n > 1 ? (T - 1) / (n - 1) : 0;

    const out = [];
    for (let k = 0; k < n; k++) {
      let x = k * step;
      if (k === n - 1) x = T - 1; // np.linspace forces the exact endpoint
      const vec = new Float32Array(D);
      if (x <= 0) {
        vec.set(arr[0]);
      } else if (x >= T - 1) {
        vec.set(arr[T - 1]);
      } else {
        const i = Math.floor(x);
        const frac = x - i;
        const lo = arr[i];
        const hi = arr[i + 1];
        for (let c = 0; c < D; c++) vec[c] = lo[c] + (hi[c] - lo[c]) * frac;
      }
      out.push(vec);
    }
    return out;
  }

  const api = { dominantLabel, buildFeatures, resample };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") {
    window.dominantLabel = dominantLabel;
    window.buildFeatures = buildFeatures;
    window.resample = resample;
  }
})();
