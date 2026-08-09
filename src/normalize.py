"""Per-frame landmark normalization — the single source of truth for feature
layout, shared between the Python extractor and (verbatim) the browser JS port.

Keep this file dependency-light (numpy only) and side-effect free. No I/O, no
globals mutated, no MediaPipe imports. The logic here must translate 1:1 to
JavaScript, so avoid fancy numpy broadcasting tricks that don't map cleanly.

Feature layout (100 dims per frame):
    [ 0: 42)  Hand A (dominant): 21 landmarks x (x, y)
    [42: 84)  Hand B:            21 landmarks x (x, y)
    [84: 98)  Pose subset: 7 points x (x, y)
              order = [nose, L_shoulder, R_shoulder, L_elbow, R_elbow,
                       L_wrist, R_wrist]
    [98]      hand A present flag (0/1)
    [99]      hand B present flag (0/1)
z is dropped entirely. A missing hand is zeros + flag 0.
"""

from __future__ import annotations

import numpy as np

NUM_HAND_LMS = 21
NUM_POSE_PTS = 7
HAND_BLOCK = NUM_HAND_LMS * 2  # 42
FEATURE_DIM = 100
SCALE_EPS = 1e-6

# Indices into the 7-point pose subset.
POSE_NOSE = 0
POSE_L_SHOULDER = 1
POSE_R_SHOULDER = 2

# An all-NaN vector is the "invalid frame" sentinel. The caller detects it and
# carries forward the previous valid frame (or zeros if none yet). No NaN ever
# survives into the saved features.
_INVALID = np.full(FEATURE_DIM, np.nan, dtype=np.float32)


def normalize_frame(hands, pose) -> np.ndarray:
    """Normalize one frame's landmarks into a fixed (100,) float32 vector.

    Parameters
    ----------
    hands : sequence of length 2
        ``hands[0]`` is hand A (dominant slot), ``hands[1]`` is hand B. Each is
        either an array-like of shape (21, 2) with raw (x, y) image coords, or
        ``None`` when that hand was not detected.
    pose : array-like (7, 2) or None
        The 7-point pose subset in raw (x, y) coords, or ``None`` if no pose was
        detected this frame.

    Returns
    -------
    np.ndarray, shape (100,), dtype float32
        The normalized feature vector, or an all-NaN sentinel if the frame is
        invalid (no pose, or the two shoulders coincide so scale ~ 0).

    Normalization (exact order):
        1. origin = midpoint of L/R shoulder
        2. scale  = euclidean distance between L/R shoulder
        3. if scale < 1e-6 -> invalid frame (all-NaN sentinel)
        4. every coord: (p - origin) / scale
    """
    if pose is None:
        return _INVALID.copy()

    pose = np.asarray(pose, dtype=np.float64).reshape(NUM_POSE_PTS, 2)
    l_sh = pose[POSE_L_SHOULDER]
    r_sh = pose[POSE_R_SHOULDER]

    origin = (l_sh + r_sh) / 2.0
    dx = l_sh[0] - r_sh[0]
    dy = l_sh[1] - r_sh[1]
    scale = float(np.sqrt(dx * dx + dy * dy))
    if scale < SCALE_EPS:
        return _INVALID.copy()

    out = np.zeros(FEATURE_DIM, dtype=np.float32)

    for i in range(2):
        hand = hands[i] if hands is not None and i < len(hands) else None
        if hand is None:
            continue  # zeros already; presence flag stays 0
        hand = np.asarray(hand, dtype=np.float64).reshape(NUM_HAND_LMS, 2)
        norm = (hand - origin) / scale
        out[i * HAND_BLOCK:(i + 1) * HAND_BLOCK] = norm.reshape(-1).astype(np.float32)
        out[98 + i] = 1.0

    pose_norm = (pose - origin) / scale
    out[84:98] = pose_norm.reshape(-1).astype(np.float32)

    return out
