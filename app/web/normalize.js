// Verbatim port of src/normalize.py — same order of operations, same constants.
// NO dependencies. Do not "improve" or refactor: parity with the Python
// pipeline is the whole point (see app/web/parity.test.js).
//
// Feature layout (100 dims per frame):
//   [ 0: 42)  Hand A (dominant): 21 landmarks x (x, y)
//   [42: 84)  Hand B:            21 landmarks x (x, y)
//   [84: 98)  Pose subset: 7 points x (x, y)
//             order = [nose, L_shoulder, R_shoulder, L_elbow, R_elbow,
//                      L_wrist, R_wrist]
//   [98]      hand A present flag (0/1)
//   [99]      hand B present flag (0/1)
// z is dropped entirely. A missing hand is zeros + flag 0.

const NUM_HAND_LMS = 21;
const NUM_POSE_PTS = 7;
const HAND_BLOCK = NUM_HAND_LMS * 2; // 42
const FEATURE_DIM = 100;
const SCALE_EPS = 1e-6;

const POSE_L_SHOULDER = 1;
const POSE_R_SHOULDER = 2;

// Normalize one frame's landmarks into a fixed (100,) Float32Array.
//
//   hands : [handA, handB]; each is an array of 21 [x, y] pairs, or null.
//   pose  : array of 7 [x, y] pairs, or null.
//
// Returns a Float32Array(100); an all-NaN vector is the "invalid frame"
// sentinel (no pose, or the two shoulders coincide so scale ~ 0). The caller
// is responsible for carry-forward.
function normalizeFrame(hands, pose) {
  const out = new Float32Array(FEATURE_DIM); // zeros

  if (pose === null || pose === undefined) {
    out.fill(NaN);
    return out;
  }

  const lSh = pose[POSE_L_SHOULDER];
  const rSh = pose[POSE_R_SHOULDER];

  const originX = (lSh[0] + rSh[0]) / 2.0;
  const originY = (lSh[1] + rSh[1]) / 2.0;
  const dx = lSh[0] - rSh[0];
  const dy = lSh[1] - rSh[1];
  const scale = Math.sqrt(dx * dx + dy * dy);
  if (scale < SCALE_EPS) {
    out.fill(NaN);
    return out;
  }

  for (let i = 0; i < 2; i++) {
    const hand = hands ? hands[i] : null;
    if (hand === null || hand === undefined) {
      continue; // zeros already; presence flag stays 0
    }
    const base = i * HAND_BLOCK;
    for (let k = 0; k < NUM_HAND_LMS; k++) {
      out[base + k * 2] = (hand[k][0] - originX) / scale;
      out[base + k * 2 + 1] = (hand[k][1] - originY) / scale;
    }
    out[98 + i] = 1.0;
  }

  for (let k = 0; k < NUM_POSE_PTS; k++) {
    out[84 + k * 2] = (pose[k][0] - originX) / scale;
    out[84 + k * 2 + 1] = (pose[k][1] - originY) / scale;
  }

  return out;
}

// Dual environment export: Node (tests) and browser (<script> global).
if (typeof module !== "undefined" && module.exports) {
  module.exports = { normalizeFrame, FEATURE_DIM, NUM_HAND_LMS, NUM_POSE_PTS, SCALE_EPS };
}
if (typeof window !== "undefined") {
  window.normalizeFrame = normalizeFrame;
  window.FEATURE_DIM = FEATURE_DIM;
}
