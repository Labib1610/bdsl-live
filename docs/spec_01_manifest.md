# Spec 01 — Build trial manifest

## Goal
Parse BdSLW60 annotation JSONs into a single validated manifest, one row per trial.

## Input
`data/raw/bdslw60/` (symlink to the dataset root). 30 folders named `W{a}-{b}`,
each containing `output1.json`, `annotation*.txt` (ignore), and `*.mp4`.

`output1.json` structure:
```
{ "W11": { "U1": { "LeftHand": { "U1W11F": {
      "User","Orientation","Session","View","FrameRate","FileName",
      "no_of_trials",
      "trials": { "0": {"starting": int, "ending": int}, ... }
}}}}}
```

## Output
`data/manifest.parquet` — one row per trial:

| column | type | notes |
|---|---|---|
| trial_id | str | `{file_stem}_t{idx:02d}` |
| video_path | str | relative to raw root |
| word_id | str | e.g. `W11` |
| label_idx | int | from vocabulary.json |
| signer_id | str | e.g. `U1` |
| orientation | str | LeftHand / RightHand |
| session | str | |
| view | str | |
| fps | float | from JSON FrameRate |
| start_frame | int | |
| end_frame | int | |
| n_frames | int | end - start |
| duration_s | float | n_frames / fps |
| source | str | constant `bdslw60` |
| split | str | leave empty; assigned later |

`data/vocabulary.json` — `{word_id: label_idx}`, sorted by numeric part of word_id.
Must contain exactly 60 entries.

`reports/manifest_summary.md` — trials per signer, per word, orientation
distribution, fps distribution, duration histogram (10 buckets), anomaly list.

## Validation (log, don't crash)
- video file referenced by FileName exists → else skip + log
- `starting < ending` → else skip + log
- `n_frames` between 10 and 300 → else flag but keep
- `no_of_trials` matches len(trials) → else log mismatch
- files not matching `U{n}W{n}F.mp4` → skip + log (expect exactly 4)

## Constraints
- Python 3.12, pandas + pyarrow only. No video decoding.
- Deterministic: sort all iteration order.
- Pure function `parse_output_json(path) -> list[dict]`, unit-testable.
- Print a summary table to stdout on completion.

## Acceptance
- manifest.parquet has between 9000 and 9400 rows
- exactly 60 unique word_ids, exactly 18 unique signer_ids
- vocabulary.json has 60 entries
- no nulls in any column except `split`