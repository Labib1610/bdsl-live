"""Render a landmark .npz (48, 100) sequence as a stick-figure debug video.

Draws the two hands (finger topology) and the pose subset
(shoulders/elbows/wrists + nose) per frame, overlays the trial metadata, and
writes an mp4 at 10 fps. Handy for eyeballing extraction / mirroring quality.

Usage:
    python scripts/render_sequence.py data/landmarks/val/U2W11F_t00.npz --out out.mp4
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

# Feature layout (see src/normalize.py): hand A [0:42), hand B [42:84),
# pose 7pts [84:98), presence flags [98], [99].
HAND_A = slice(0, 42)
HAND_B = slice(42, 84)
POSE = slice(84, 98)
FLAG_A, FLAG_B = 98, 99

# MediaPipe 21-landmark hand topology.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),                                 # palm base
]

# Pose subset order: 0 nose, 1 L_sh, 2 R_sh, 3 L_elbow, 4 R_elbow, 5 L_wrist, 6 R_wrist
POSE_CONNECTIONS = [(1, 2), (1, 3), (3, 5), (2, 4), (4, 6)]

CANVAS = 512
MARGIN = 70
FPS = 10
COLOR_A = (0, 220, 0)      # hand A (dominant) — green
COLOR_B = (0, 165, 255)    # hand B — orange
COLOR_POSE = (255, 180, 0)  # pose — blue
BG = (24, 24, 24)


def _hand_pts(frame: np.ndarray, sl: slice) -> np.ndarray:
    return frame[sl].reshape(21, 2)


def _pose_pts(frame: np.ndarray) -> np.ndarray:
    return frame[POSE].reshape(7, 2)


def _fit_transform(features: np.ndarray):
    """Compute a single (scale, offset) mapping normalized coords -> canvas px,
    fit over every drawn point across all frames so nothing clips."""
    pts = []
    for f in features:
        pts.append(_pose_pts(f))
        if f[FLAG_A] > 0.5:
            pts.append(_hand_pts(f, HAND_A))
        if f[FLAG_B] > 0.5:
            pts.append(_hand_pts(f, HAND_B))
    allpts = np.concatenate(pts, axis=0)
    lo = allpts.min(axis=0)
    hi = allpts.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    scale = (CANVAS - 2 * MARGIN) / span.max()  # uniform scale, preserve aspect
    # center the content
    content = (hi + lo) / 2.0
    offset = np.array([CANVAS / 2.0, CANVAS / 2.0]) - content * scale
    return scale, offset


def _to_px(pt, scale, offset):
    xy = pt * scale + offset
    return int(round(xy[0])), int(round(xy[1]))


def _draw_edges(img, pts, connections, scale, offset, color):
    for a, b in connections:
        cv2.line(img, _to_px(pts[a], scale, offset), _to_px(pts[b], scale, offset), color, 2, cv2.LINE_AA)
    for p in pts:
        cv2.circle(img, _to_px(p, scale, offset), 3, color, -1, cv2.LINE_AA)


def _overlay_text(img, lines):
    y = 22
    for text in lines:
        cv2.putText(img, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(img, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        y += 20


def render(npz_path: Path, out_path: Path) -> None:
    data = np.load(npz_path, allow_pickle=False)
    features = data["features"].astype(np.float32)
    if features.shape != (48, 100):
        raise ValueError(f"expected (48, 100) features, got {features.shape}")

    meta = {
        "signer_id": str(data["signer_id"]),
        "word_id": str(data["word_id"]),
        "orientation_annotated": str(data["orientation_annotated"]),
        "orientation_detected": str(data["orientation_detected"]),
    }
    header = [
        f"{meta['word_id']}  signer={meta['signer_id']}",
        f"annotated={meta['orientation_annotated']}  detected={meta['orientation_detected']}",
    ]

    scale, offset = _fit_transform(features)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (CANVAS, CANVAS))
    if not writer.isOpened():
        raise RuntimeError(f"could not open VideoWriter for {out_path}")

    for i, frame in enumerate(features):
        img = np.full((CANVAS, CANVAS, 3), BG, dtype=np.uint8)
        _draw_edges(img, _pose_pts(frame), POSE_CONNECTIONS, scale, offset, COLOR_POSE)
        if frame[FLAG_A] > 0.5:
            _draw_edges(img, _hand_pts(frame, HAND_A), HAND_CONNECTIONS, scale, offset, COLOR_A)
        if frame[FLAG_B] > 0.5:
            _draw_edges(img, _hand_pts(frame, HAND_B), HAND_CONNECTIONS, scale, offset, COLOR_B)
        _overlay_text(img, header + [f"frame {i + 1}/48"])
        writer.write(img)

    writer.release()
    print(f"rendered {npz_path.name} -> {out_path} ({features.shape[0]} frames @ {FPS} fps)")
    for k, v in meta.items():
        print(f"  {k:22} {v}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a landmark npz as a stick-figure mp4.")
    ap.add_argument("npz", type=Path, help="path to a data/landmarks/**/**.npz file")
    ap.add_argument("--out", type=Path, required=True, help="output .mp4 path")
    args = ap.parse_args()
    render(args.npz, args.out)


if __name__ == "__main__":
    main()
