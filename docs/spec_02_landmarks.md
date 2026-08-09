# Spec 02 — Landmark extraction

## Goal
Decode each manifest trial, run MediaPipe Tasks, emit fixed-shape normalized
feature tensors. Write `configs/splits.yaml` and assign splits in the manifest.

## Part A — splits.yaml
Create `configs/splits.yaml` (hand-written constant, do not derive):
```yaml
train:    [U1, U3, U4, U5, U6, U8, U9, U11, U12, U15]
val:      [U2, U13]
heldout:  [U10, U14, U16, U17, U18, U7]
```
Assign `split` column in manifest from this. Excluded trials get `split="excluded"`
and are NOT extracted.

Exclusion rule: `n_frames < 8` OR `n_frames < 0.4 * (median n_frames for that word_id)`.
Expect ~148 excluded.

## Part B — extraction

For each non-excluded trial:
1. Decode frames `[start_frame, end_frame]` from `video_path` (OpenCV).
2. Downscale to 640px on the long edge before landmarking.
3. Run MediaPipe Tasks HandLandmarker (max 2 hands) + PoseLandmarker per frame.
4. Build the raw per-frame array (see Feature spec).
5. Normalize (see Normalization).
6. Mirror if left-dominant (see Mirroring).
7. Resample the frame axis to exactly 48 via linear interpolation.
8. Save `data/landmarks/{split}/{trial_id}.npz` with keys:
   - `features` float32 `(48, 100)`
   - `label_idx` int
   - `signer_id`, `word_id`, `orientation_annotated`, `orientation_detected` str
   - `n_frames_original` int
   - `hand_presence_rate` float — fraction of frames with ≥1 hand detected

## Feature spec (100 dims/frame)
- Hand A (dominant): 21 landmarks × (x, y) = 42
- Hand B: 21 × (x, y) = 42
- Pose subset, 7 points × (x, y) = 14 — nose, L/R shoulder, L/R elbow, L/R wrist
- 2 presence flags: hand A present, hand B present
Total 100. Drop z entirely. Missing hand → zeros + flag 0.

## Normalization
Per frame, in this exact order:
1. origin = midpoint of L/R shoulder
2. scale = euclidean distance between L/R shoulder
3. if scale < 1e-6 → mark frame invalid, carry forward previous valid frame
4. all coords: `(p - origin) / scale`
Emit `src/normalize.py` with a single pure function
`normalize_frame(hands, pose) -> np.ndarray(100,)`. This file will be
ported to JS verbatim — keep it dependency-light and side-effect free.

## Mirroring
Determine dominant hand from MediaPipe handedness across the trial (majority vote
over frames where exactly one hand is present; if two hands throughout, use the
hand with greater total wrist displacement).
Record as `orientation_detected`.
If dominant == Left: negate all x AFTER normalization, and swap hand A/B arrays.
Result: every stored sample is right-dominant canonical.

## Part C — reports
`reports/extraction_summary.md`:
- trials attempted / succeeded / failed, with failure reasons
- `hand_presence_rate` distribution (deciles)
- trials with presence rate < 0.5 (candidate bad extractions)
- **orientation agreement**: crosstab `orientation_annotated` vs `orientation_detected`,
  and overall disagreement rate
- per-split, per-word counts
- wall-clock time

## Constraints
- Python 3.12. opencv-python, mediapipe, numpy, pandas.
- MediaPipe **Tasks** API. Download .task model files to `models/`, gitignored.
- Resumable: skip trials whose .npz already exists. `--force` to override.
- `--limit N` flag for smoke testing.
- Deterministic given the same inputs.
- Process pool over videos, not frames. Default workers = cpu_count // 2.
- Progress bar with ETA.

## Acceptance
- ~9,119 npz files across the three split dirs
- every `features` array is exactly (48, 100) float32, no NaN/inf
- `--limit 20` completes in under 2 minutes
- rerunning without `--force` skips everything and exits fast