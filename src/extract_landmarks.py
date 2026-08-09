"""Part B/C — decode manifest trials, run MediaPipe Tasks, emit (48, 100) tensors.

For every non-excluded trial we decode frames [start, end], run HandLandmarker
(<=2 hands) + PoseLandmarker per frame, build/normalize/mirror the feature array
(see src/normalize.py), resample the time axis to 48, and save one npz under
data/landmarks/{split}/{trial_id}.npz.

Runs a process pool over videos (not frames). Resumable: existing npz are
skipped unless --force. --limit N processes only the first N trials (by
trial_id) for smoke tests.
"""

from __future__ import annotations

import os

# Quiet the very chatty MediaPipe / TFLite C++ logging before anything imports it.
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from normalize import FEATURE_DIM, normalize_frame

TARGET_FRAMES = 48
LONG_EDGE = 640
# pose subset order: nose, L/R shoulder, L/R elbow, L/R wrist
POSE_SUBSET = (0, 11, 12, 13, 14, 15, 16)
WRIST_LM = 0  # hand landmark index used for displacement / tracking

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RAW = REPO / "data" / "raw" / "bdslw60"
DEFAULT_OUT = REPO / "data" / "landmarks"
DEFAULT_MANIFEST = REPO / "data" / "manifest.parquet"
DEFAULT_REPORT = REPO / "reports" / "extraction_summary.md"
HAND_MODEL = REPO / "models" / "hand_landmarker.task"
POSE_MODEL = REPO / "models" / "pose_landmarker_lite.task"

# Per-worker global detectors (built once in the pool initializer).
_HANDS = None
_POSE = None


def _init_worker(hand_model: str, pose_model: str) -> None:
    global _HANDS, _POSE
    from mediapipe.tasks import python as mptp
    from mediapipe.tasks.python import vision

    base = mptp.BaseOptions
    _HANDS = vision.HandLandmarker.create_from_options(
        vision.HandLandmarkerOptions(
            base_options=base(model_asset_path=hand_model),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
        )
    )
    _POSE = vision.PoseLandmarker.create_from_options(
        vision.PoseLandmarkerOptions(
            base_options=base(model_asset_path=pose_model),
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
        )
    )


def _downscale(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    long_edge = max(h, w)
    if long_edge <= LONG_EDGE:
        return frame
    s = LONG_EDGE / long_edge
    return cv2.resize(frame, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)


def _decode(video_path: Path, start: int, end: int) -> list[np.ndarray]:
    """Decode frames [start, end] inclusive; returns [] if the video won't open."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    for _ in range(start, end + 1):
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    return frames


def _detect_frame(rgb: np.ndarray):
    """Return (hand_map, pose_subset) for one RGB frame.

    hand_map: dict label('Left'/'Right') -> np.ndarray(21, 2)  (only detected hands)
    pose_subset: np.ndarray(7, 2) or None
    """
    import mediapipe as mp

    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
    hres = _HANDS.detect(image)
    pres = _POSE.detect(image)

    hand_map: dict[str, np.ndarray] = {}
    for lms, handed in zip(hres.hand_landmarks, hres.handedness):
        label = handed[0].category_name  # 'Left' or 'Right'
        if label in hand_map:
            continue  # keep the first hand for a duplicated label (rare)
        hand_map[label] = np.array([[lm.x, lm.y] for lm in lms], dtype=np.float64)

    pose_subset = None
    if pres.pose_landmarks:
        p = pres.pose_landmarks[0]
        pose_subset = np.array([[p[i].x, p[i].y] for i in POSE_SUBSET], dtype=np.float64)

    return hand_map, pose_subset


def _dominant_label(hand_maps: list[dict]) -> str:
    """Trial-level dominant hand: majority over single-hand frames; else the hand
    with greater total wrist displacement; else default 'Right'."""
    singles = [next(iter(m)) for m in hand_maps if len(m) == 1]
    if singles:
        left = singles.count("Left")
        right = singles.count("Right")
        if left == right:
            return "Right"  # deterministic tie-break toward canonical
        return "Left" if left > right else "Right"

    # No single-hand frame anywhere: fall back to wrist displacement.
    disp = {"Left": 0.0, "Right": 0.0}
    prev: dict[str, np.ndarray] = {}
    for m in hand_maps:
        for label, lms in m.items():
            wrist = lms[WRIST_LM]
            if label in prev:
                disp[label] += float(np.hypot(*(wrist - prev[label])))
            prev[label] = wrist
    if disp["Left"] == disp["Right"]:
        return "Right"
    return "Left" if disp["Left"] > disp["Right"] else "Right"


def _build_features(hand_maps: list[dict], poses: list, dominant: str) -> np.ndarray:
    """Assign A/B slots, normalize per frame with carry-forward, mirror if left."""
    other = "Right" if dominant == "Left" else "Left"

    vecs = []
    last_valid = None
    for hand_map, pose in zip(hand_maps, poses):
        slots = [hand_map.get(dominant), hand_map.get(other)]
        vec = normalize_frame(slots, pose)
        if np.isnan(vec).any():
            vec = last_valid.copy() if last_valid is not None else np.zeros(FEATURE_DIM, np.float32)
        else:
            last_valid = vec
        vecs.append(vec)
    arr = np.stack(vecs).astype(np.float32)  # (T, 100)

    if dominant == "Left":
        # Mirror to right-dominant canonical: negate every x coord, then swap the
        # two hand blocks (and their presence flags).
        arr[:, 0:98:2] *= -1.0
        a = arr[:, 0:42].copy()
        arr[:, 0:42] = arr[:, 42:84]
        arr[:, 42:84] = a
        fa = arr[:, 98].copy()
        arr[:, 98] = arr[:, 99]
        arr[:, 99] = fa

    return arr


def _resample(arr: np.ndarray, n: int = TARGET_FRAMES) -> np.ndarray:
    t = arr.shape[0]
    old = np.arange(t, dtype=np.float64)
    new = np.linspace(0.0, t - 1, n)
    out = np.empty((n, arr.shape[1]), dtype=np.float32)
    for c in range(arr.shape[1]):
        out[:, c] = np.interp(new, old, arr[:, c])
    return out


def process_trial(job: dict) -> dict:
    """Worker entry point. Decodes, extracts, and writes one npz."""
    out_path = Path(job["out_path"])
    result = {
        "trial_id": job["trial_id"],
        "split": job["split"],
        "word_id": job["word_id"],
        "orientation_annotated": job["orientation"],
        "status": "failed",
        "reason": "",
        "orientation_detected": "",
        "hand_presence_rate": 0.0,
        "n_frames_original": 0,
    }

    frames = _decode(Path(job["video_path"]), job["start_frame"], job["end_frame"])
    if not frames:
        result["reason"] = "no_frames_decoded"
        return result

    hand_maps, poses, present = [], [], 0
    for frame in frames:
        rgb = cv2.cvtColor(_downscale(frame), cv2.COLOR_BGR2RGB)
        hand_map, pose = _detect_frame(rgb)
        hand_maps.append(hand_map)
        poses.append(pose)
        if hand_map:
            present += 1

    dominant = _dominant_label(hand_maps)
    arr = _build_features(hand_maps, poses, dominant)
    features = _resample(arr)

    if features.shape != (TARGET_FRAMES, FEATURE_DIM) or not np.isfinite(features).all():
        result["reason"] = "non_finite_or_bad_shape"
        return result

    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        features=features,
        label_idx=np.int64(job["label_idx"]),
        signer_id=job["signer_id"],
        word_id=job["word_id"],
        orientation_annotated=job["orientation"],
        orientation_detected="LeftHand" if dominant == "Left" else "RightHand",
        n_frames_original=np.int64(len(frames)),
        hand_presence_rate=np.float32(present / len(frames)),
    )

    result.update(
        status="ok",
        orientation_detected="LeftHand" if dominant == "Left" else "RightHand",
        hand_presence_rate=present / len(frames),
        n_frames_original=len(frames),
    )
    return result


def _read_npz_meta(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {
            "trial_id": path.stem,
            "split": path.parent.name,
            "word_id": str(z["word_id"]),
            "orientation_annotated": str(z["orientation_annotated"]),
            "orientation_detected": str(z["orientation_detected"]),
            "hand_presence_rate": float(z["hand_presence_rate"]),
            "n_frames_original": int(z["n_frames_original"]),
            "status": "ok",
        }


def write_report(rows: list[dict], attempted: int, succeeded: int, failures: list[dict],
                 skipped: int, elapsed: float, out_path: Path) -> None:
    df = pd.DataFrame(rows)
    lines = ["# BdSLW60 landmark extraction summary", ""]
    lines += [
        f"- Trials selected: **{len(rows) + len(failures)}** "
        f"(newly attempted {attempted}, skipped existing {skipped})",
        f"- Succeeded: **{succeeded + skipped}**",
        f"- Failed: **{len(failures)}**",
        f"- Wall-clock (extraction): **{elapsed:.1f}s**",
        "",
    ]

    lines += ["## Failures", ""]
    if not failures:
        lines.append("_None._")
    else:
        lines += ["| trial_id | reason |", "|---|---|"]
        by_reason: dict[str, int] = {}
        for f in failures:
            by_reason[f["reason"]] = by_reason.get(f["reason"], 0) + 1
        for f in sorted(failures, key=lambda x: x["trial_id"]):
            lines.append(f"| {f['trial_id']} | {f['reason']} |")
        lines += ["", "Reason counts: " + ", ".join(f"{k}={v}" for k, v in sorted(by_reason.items()))]
    lines.append("")

    if not df.empty:
        rate = df["hand_presence_rate"]
        lines += ["## Hand presence rate — deciles", "", "| decile | value |", "|---|---|"]
        for d in range(0, 11):
            lines.append(f"| p{d*10} | {rate.quantile(d/10):.3f} |")
        lines.append("")

        low = df[df["hand_presence_rate"] < 0.5].sort_values("hand_presence_rate")
        lines += [f"## Candidate bad extractions (presence rate < 0.5): {len(low)}", ""]
        if len(low):
            lines += ["| trial_id | split | word | presence |", "|---|---|---|---|"]
            for _, r in low.iterrows():
                lines.append(
                    f"| {r.trial_id} | {r.split} | {r.word_id} | {r.hand_presence_rate:.3f} |"
                )
        lines.append("")

        ct = pd.crosstab(df["orientation_annotated"], df["orientation_detected"])
        disagree = int((df["orientation_annotated"] != df["orientation_detected"]).sum())
        lines += ["## Orientation agreement", "",
                  "Crosstab (rows = annotated, cols = detected):", "", "```",
                  ct.to_string(), "```", "",
                  f"Overall disagreement rate: **{disagree}/{len(df)} = {disagree/len(df):.3f}**", ""]

        lines += ["## Per-split / per-word counts", "", "Per split:", "", "```",
                  df["split"].value_counts().to_string(), "```", ""]
        lines += ["<details><summary>Per split x word</summary>", "", "```",
                  df.groupby(["split", "word_id"]).size().to_string(), "```", "", "</details>", ""]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract MediaPipe landmark tensors.")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--raw-root", type=Path, default=DEFAULT_RAW)
    ap.add_argument("--out-root", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--limit", type=int, default=None, help="process only first N trials")
    ap.add_argument("--force", action="store_true", help="re-extract even if npz exists")
    args = ap.parse_args()

    df = pd.read_parquet(args.manifest)
    todo = df[df["split"] != "excluded"].sort_values("trial_id").reset_index(drop=True)
    if args.limit is not None:
        todo = todo.head(args.limit)

    jobs, skipped_meta = [], []
    for _, r in todo.iterrows():
        out_path = args.out_root / r["split"] / f"{r['trial_id']}.npz"
        if out_path.exists() and not args.force:
            skipped_meta.append(out_path)
            continue
        jobs.append({
            "trial_id": r["trial_id"],
            "video_path": str(args.raw_root / r["video_path"]),
            "start_frame": int(r["start_frame"]),
            "end_frame": int(r["end_frame"]),
            "label_idx": int(r["label_idx"]),
            "signer_id": r["signer_id"],
            "word_id": r["word_id"],
            "orientation": r["orientation"],
            "split": r["split"],
            "out_path": str(out_path),
        })

    print(f"selected {len(todo)} trials | to process {len(jobs)} | skip existing {len(skipped_meta)}")

    results, failures = [], []
    start = time.time()
    if jobs:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=_init_worker,
            initargs=(str(HAND_MODEL), str(POSE_MODEL)),
        ) as ex:
            futs = [ex.submit(process_trial, j) for j in jobs]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="extract", unit="trial"):
                res = fut.result()
                if res["status"] == "ok":
                    results.append(res)
                else:
                    failures.append(res)
    elapsed = time.time() - start

    # Include already-existing npz in the report so reruns still summarize fully.
    for path in skipped_meta:
        try:
            results.append(_read_npz_meta(path))
        except Exception:
            pass

    write_report(results, attempted=len(jobs), succeeded=len(results) - len(skipped_meta),
                 failures=failures, skipped=len(skipped_meta), elapsed=elapsed, out_path=args.report)

    print(f"\ndone in {elapsed:.1f}s | ok {len([r for r in results])} | failed {len(failures)}")
    print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
