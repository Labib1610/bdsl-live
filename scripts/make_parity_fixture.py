"""Part A — build parity fixtures for the JS normalize port.

Picks 3 trials, re-runs MediaPipe to get RAW (pre-normalization) hand+pose
landmark arrays per frame, and records the expected per-frame normalized output
from src/normalize.py. app/web/parity.test.js replays these through
normalize.js and asserts agreement.

Only frames with a valid pose are kept (so no NaN sentinels land in the JSON),
then a fixed 48 are selected by nearest-neighbour sampling — giving a clean
(48, 100) expected array without interpolating any landmark coordinates.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import extract_landmarks as ex  # noqa: E402
from normalize import SCALE_EPS, normalize_frame  # noqa: E402

N_TRIALS = 3
N_FRAMES = 48
MIN_DECODE = 60  # pick trials with plenty of frames so >=48 have valid pose
FIX_DIR = REPO / "app" / "web" / "fixtures"


def _pose_scale_ok(pose: np.ndarray) -> bool:
    dx = pose[1][0] - pose[2][0]
    dy = pose[1][1] - pose[2][1]
    return float(np.sqrt(dx * dx + dy * dy)) >= SCALE_EPS


def build_fixture(row, raw_root: Path) -> dict | None:
    video = raw_root / row["video_path"]
    frames = ex._decode(video, int(row["start_frame"]), int(row["end_frame"]))
    if not frames:
        return None

    per_frame = []
    for frame in frames:
        rgb = cv2.cvtColor(ex._downscale(frame), cv2.COLOR_BGR2RGB)
        hand_map, pose = ex._detect_frame(rgb)
        per_frame.append((hand_map, pose))

    dominant = ex._dominant_label([hm for hm, _ in per_frame])
    other = "Right" if dominant == "Left" else "Left"

    valid = [(hm, pose) for hm, pose in per_frame if pose is not None and _pose_scale_ok(pose)]
    if len(valid) < N_FRAMES:
        return None

    idxs = np.round(np.linspace(0, len(valid) - 1, N_FRAMES)).astype(int)
    frames_json, expected = [], []
    for i in idxs:
        hand_map, pose = valid[i]
        hand_a = hand_map.get(dominant)
        hand_b = hand_map.get(other)
        vec = normalize_frame([hand_a, hand_b], pose)
        assert np.isfinite(vec).all(), "unexpected NaN in fixture expected output"
        frames_json.append({
            "handA": hand_a.tolist() if hand_a is not None else None,
            "handB": hand_b.tolist() if hand_b is not None else None,
            "pose": pose.tolist(),
        })
        expected.append([float(x) for x in vec])

    return {
        "trial_id": row["trial_id"],
        "dominant": dominant,
        "n_frames": N_FRAMES,
        "feature_dim": len(expected[0]),
        "frames": frames_json,
        "expected": expected,
    }


def build_pipeline_fixture(row, raw_root: Path) -> dict | None:
    """Full-segment fixture: raw per-frame hand maps + poses, and the expected
    (48, 100) after the whole extract pipeline (dominant -> normalize +
    carry-forward -> left mirror -> resample). Exercises resample and mirror."""
    video = raw_root / row["video_path"]
    frames = ex._decode(video, int(row["start_frame"]), int(row["end_frame"]))
    if not frames:
        return None

    hand_maps, poses = [], []
    for frame in frames:
        rgb = cv2.cvtColor(ex._downscale(frame), cv2.COLOR_BGR2RGB)
        hand_map, pose = ex._detect_frame(rgb)
        hand_maps.append(hand_map)
        poses.append(pose)

    dominant = ex._dominant_label(hand_maps)
    arr = ex._build_features(hand_maps, poses, dominant)  # (T, 100)
    out = ex._resample(arr, ex.TARGET_FRAMES)             # (48, 100)

    frames_json = [
        {
            "hands": {label: lms.tolist() for label, lms in hand_map.items()},
            "pose": pose.tolist() if pose is not None else None,
        }
        for hand_map, pose in zip(hand_maps, poses)
    ]
    return {
        "trial_id": row["trial_id"],
        "dominant": dominant,
        "n_frames_segment": len(frames),
        "target_frames": ex.TARGET_FRAMES,
        "frames": frames_json,
        "expected": [[float(x) for x in vec] for vec in out],
    }


def _row_for_trial(df: pd.DataFrame, trial_id: str):
    hit = df[df["trial_id"] == trial_id]
    return hit.iloc[0] if len(hit) else None


def _first_left_dominant_trial() -> str | None:
    """Cheap scan of extracted npz for a Left-dominant trial (to cover mirror)."""
    for npz in sorted(glob.glob(str(REPO / "data" / "landmarks" / "*" / "*.npz"))):
        z = np.load(npz, allow_pickle=False)
        if str(z["orientation_detected"]) == "LeftHand":
            return Path(npz).stem
    return None


def _select_pipeline_trials(df: pd.DataFrame) -> list:
    """Pick trials covering: left-dominant (mirror), short (upsample), long (downsample)."""
    non_excl = df[df["split"] != "excluded"].copy()
    non_excl["seg"] = non_excl["end_frame"] - non_excl["start_frame"]
    picks, used = [], set()

    left_id = _first_left_dominant_trial()
    if left_id is not None:
        row = _row_for_trial(non_excl, left_id)
        if row is not None:
            picks.append(row); used.add(left_id)

    short = non_excl[(non_excl["seg"] >= 10) & (non_excl["seg"] <= 30) &
                     (~non_excl["trial_id"].isin(used))].sort_values("trial_id")
    if len(short):
        picks.append(short.iloc[0]); used.add(short.iloc[0]["trial_id"])

    long_ = non_excl[(non_excl["seg"] >= 80) &
                     (~non_excl["trial_id"].isin(used))].sort_values("trial_id")
    if len(long_):
        picks.append(long_.iloc[0]); used.add(long_.iloc[0]["trial_id"])
    return picks


def main() -> None:
    ex._init_worker(str(ex.HAND_MODEL), str(ex.POSE_MODEL))
    raw_root = ex.DEFAULT_RAW

    df = pd.read_parquet(REPO / "data" / "manifest.parquet")
    FIX_DIR.mkdir(parents=True, exist_ok=True)

    # --- per-frame normalize fixtures (normalize.js) ---
    cand = df[(df["split"] != "excluded") &
              ((df["end_frame"] - df["start_frame"]) >= MIN_DECODE)].sort_values("trial_id")
    written = 0
    for _, row in cand.iterrows():
        if written >= N_TRIALS:
            break
        fixture = build_fixture(row, raw_root)
        if fixture is None:
            continue
        out = FIX_DIR / f"{row['trial_id']}.json"
        out.write_text(json.dumps(fixture))
        print(f"wrote {out.relative_to(REPO)}  ({fixture['n_frames']}x{fixture['feature_dim']}, "
              f"dominant={fixture['dominant']})")
        written += 1
    if written < N_TRIALS:
        raise SystemExit(f"only built {written}/{N_TRIALS} normalize fixtures")

    # --- full-pipeline fixtures (pipeline.js: dominant + mirror + resample) ---
    pipe_written = 0
    for row in _select_pipeline_trials(df):
        fixture = build_pipeline_fixture(row, raw_root)
        if fixture is None:
            continue
        out = FIX_DIR / f"pipeline_{row['trial_id']}.json"
        out.write_text(json.dumps(fixture))
        direction = ("upsample" if fixture["n_frames_segment"] < ex.TARGET_FRAMES
                     else "downsample" if fixture["n_frames_segment"] > ex.TARGET_FRAMES else "equal")
        print(f"wrote {out.relative_to(REPO)}  (T={fixture['n_frames_segment']}->48 {direction}, "
              f"dominant={fixture['dominant']})")
        pipe_written += 1
    if pipe_written == 0:
        raise SystemExit("built no pipeline fixtures")

    print(f"done: {written} normalize + {pipe_written} pipeline fixtures in {FIX_DIR.relative_to(REPO)}")


if __name__ == "__main__":
    main()
