Fix two train/serve mismatches in app/web/app.js:

1. Segment-and-resample. Replace the fixed rolling window with: buffer normalized frames while ≥1 hand is present; when hand presence is absent for 5 consecutive frames AND the buffer has ≥8 frames, resample the buffer to exactly 48 frames by linear interpolation (identical to src/extract_landmarks.py), compute first-diffs, run inference once, then clear the buffer. Show a visual "recording / idle" state so the user knows when a sign is being captured.

2. Mirroring. Apply the same left-dominant canonicalization as extraction: determine dominant hand by majority vote over frames with exactly one hand, and if Left, negate x after normalization and swap hand A/B — matching src/extract_landmarks.py exactly.

Extend parity.test.js to cover the resample and mirror steps against Python fixtures.