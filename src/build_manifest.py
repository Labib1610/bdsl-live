"""Build a validated trial manifest from BdSLW60 annotation JSONs.

Parses every ``output1.json`` under the raw dataset root into a single
``manifest.parquet`` with one row per annotated trial, alongside a
``vocabulary.json`` (word_id -> label_idx) and a human-readable summary report.

Design notes
------------
* :func:`parse_output_json` is a pure, unit-testable function that turns one
  ``output1.json`` into a list of trial-row dicts. Anomalies are appended to an
  optional out-list rather than raised, so parsing never crashes on bad data.
* Iteration order is fully sorted for deterministic output.
* No video is ever decoded; frame counts come straight from the annotations.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

SOURCE = "bdslw60"
FILENAME_RE = re.compile(r"U\d+W\d+F")
N_FRAMES_MIN, N_FRAMES_MAX = 10, 300

# Columns in the exact manifest order. ``label_idx`` and ``split`` are filled in
# by the caller (they need the global vocabulary / a later split assignment).
MANIFEST_COLUMNS = [
    "trial_id",
    "video_path",
    "word_id",
    "label_idx",
    "signer_id",
    "orientation",
    "session",
    "view",
    "fps",
    "start_frame",
    "end_frame",
    "n_frames",
    "duration_s",
    "source",
    "split",
]


def _signer_num(signer: str) -> int:
    """Sort key for signer ids like ``U1`` .. ``U18`` (numeric, not lexical)."""
    return int(signer[1:])


def _word_num(word_id: str) -> int:
    """Sort key for word ids like ``W1`` .. ``W360`` (numeric part)."""
    return int(word_id[1:])


def parse_output_json(path, anomalies: list[dict] | None = None) -> list[dict]:
    """Parse one ``output1.json`` into a list of trial-row dicts.

    Rows omit ``label_idx`` and ``split``; those are assigned globally by the
    caller. Validation issues are appended to ``anomalies`` (if provided) as
    ``{"kind", "file", "detail"}`` dicts and never raise.

    Skips (row dropped): unparsable/oddly-named ``FileName``, missing video
    file, or ``starting >= ending``. Flags (row kept): ``n_frames`` outside
    ``[10, 300]``, and ``no_of_trials`` disagreeing with ``len(trials)``.
    """
    path = Path(path)
    folder = path.parent.name
    data = json.loads(path.read_text())

    def note(kind: str, detail: str) -> None:
        if anomalies is not None:
            anomalies.append({"kind": kind, "file": folder, "detail": detail})

    # Group entries by physical file stem so that the same recording annotated
    # under two orientations (a known quirk of this dataset) shares one
    # contiguous trial-index space and never yields duplicate trial_ids.
    entries_by_stem: dict[str, list[tuple[str, str, str, dict]]] = {}
    for word_id in sorted(data):
        for signer in sorted(data[word_id], key=_signer_num):
            for orientation in sorted(data[word_id][signer]):
                block = data[word_id][signer][orientation]
                for _key, meta in sorted(block.items()):
                    stem = str(meta.get("FileName"))
                    entries_by_stem.setdefault(stem, []).append(
                        (word_id, signer, orientation, meta)
                    )

    rows: list[dict] = []
    for stem in sorted(entries_by_stem):
        entries = entries_by_stem[stem]

        if not FILENAME_RE.fullmatch(stem):
            n = sum(len(m.get("trials", {})) for *_r, m in entries)
            note("bad_filename", f"{stem} (skipped {n} trial(s))")
            continue

        video_rel = f"{folder}/{stem}.mp4"
        if not (path.parent / f"{stem}.mp4").exists():
            n = sum(len(m.get("trials", {})) for *_r, m in entries)
            note("missing_video", f"{video_rel} (skipped {n} trial(s))")
            continue

        idx = 0
        for word_id, signer, orientation, meta in entries:
            trials = meta.get("trials", {}) or {}

            raw_declared = meta.get("no_of_trials")
            try:
                declared = int(raw_declared)
                if declared != len(trials):
                    note(
                        "no_of_trials_mismatch",
                        f"{stem}/{orientation}: declared {declared} != {len(trials)}",
                    )
            except (TypeError, ValueError):
                note(
                    "no_of_trials_unparsable",
                    f"{stem}/{orientation}: no_of_trials={raw_declared!r} (have {len(trials)})",
                )

            fps = float(meta["FrameRate"])
            for tkey, trial in sorted(trials.items(), key=lambda kv: int(kv[0])):
                start = trial.get("starting")
                end = trial.get("ending")
                if start is None or end is None or start >= end:
                    note(
                        "bad_frame_range",
                        f"{stem}/{orientation} trial {tkey}: start={start} end={end}",
                    )
                    continue

                n_frames = end - start
                if not (N_FRAMES_MIN <= n_frames <= N_FRAMES_MAX):
                    note(
                        "n_frames_out_of_range",
                        f"{stem}/{orientation} trial {tkey}: n_frames={n_frames}",
                    )

                rows.append(
                    {
                        "trial_id": f"{stem}_t{idx:02d}",
                        "video_path": video_rel,
                        "word_id": word_id,
                        "signer_id": signer,
                        "orientation": orientation,
                        "session": str(meta["Session"]),
                        "view": str(meta["View"]),
                        "fps": fps,
                        "start_frame": int(start),
                        "end_frame": int(end),
                        "n_frames": int(n_frames),
                        "duration_s": n_frames / fps,
                        "source": SOURCE,
                    }
                )
                idx += 1

    return rows


def build_vocabulary(json_paths: list[Path]) -> dict[str, int]:
    """Map every word_id (top-level JSON key) to a label index, sorted by word number."""
    word_ids: set[str] = set()
    for path in json_paths:
        word_ids.update(json.loads(path.read_text()).keys())
    return {w: i for i, w in enumerate(sorted(word_ids, key=_word_num))}


def _duration_histogram(durations: pd.Series, buckets: int = 10) -> list[str]:
    lo, hi = float(durations.min()), float(durations.max())
    width = (hi - lo) / buckets if hi > lo else 1.0
    lines = []
    for b in range(buckets):
        left = lo + b * width
        right = hi if b == buckets - 1 else lo + (b + 1) * width
        if b == buckets - 1:
            count = int(((durations >= left) & (durations <= right)).sum())
        else:
            count = int(((durations >= left) & (durations < right)).sum())
        bar = "#" * int(round(40 * count / max(1, len(durations))))
        lines.append(f"[{left:5.2f}, {right:5.2f}) s | {count:5d} | {bar}")
    return lines


def write_report(df: pd.DataFrame, anomalies: list[dict], out_path: Path) -> None:
    lines: list[str] = ["# BdSLW60 manifest summary", ""]
    lines.append(f"- Total trials: **{len(df)}**")
    lines.append(f"- Unique words: **{df['word_id'].nunique()}**")
    lines.append(f"- Unique signers: **{df['signer_id'].nunique()}**")
    lines.append(f"- Total anomalies logged: **{len(anomalies)}**")
    lines.append("")

    lines.append("## Trials per signer")
    lines.append("")
    lines.append("| signer | trials |")
    lines.append("|---|---|")
    per_signer = df["signer_id"].value_counts()
    for signer in sorted(per_signer.index, key=_signer_num):
        lines.append(f"| {signer} | {int(per_signer[signer])} |")
    lines.append("")

    lines.append("## Trials per word")
    lines.append("")
    lines.append("| word | label_idx | trials |")
    lines.append("|---|---|---|")
    per_word = df.groupby("word_id").agg(label_idx=("label_idx", "first"), n=("trial_id", "size"))
    for word in sorted(per_word.index, key=_word_num):
        row = per_word.loc[word]
        lines.append(f"| {word} | {int(row['label_idx'])} | {int(row['n'])} |")
    lines.append("")

    lines.append("## Orientation distribution")
    lines.append("")
    lines.append("| orientation | trials |")
    lines.append("|---|---|")
    for orient, n in df["orientation"].value_counts().items():
        lines.append(f"| {orient} | {int(n)} |")
    lines.append("")

    lines.append("## FPS distribution")
    lines.append("")
    lines.append("| fps | trials |")
    lines.append("|---|---|")
    for fps, n in df["fps"].value_counts().sort_index().items():
        lines.append(f"| {fps:g} | {int(n)} |")
    lines.append("")

    lines.append("## Duration histogram (10 buckets)")
    lines.append("")
    lines.append("```")
    lines.extend(_duration_histogram(df["duration_s"]))
    lines.append("```")
    lines.append("")

    lines.append("## Anomalies")
    lines.append("")
    if not anomalies:
        lines.append("_None._")
    else:
        by_kind: dict[str, int] = {}
        for a in anomalies:
            by_kind[a["kind"]] = by_kind.get(a["kind"], 0) + 1
        lines.append("| kind | count |")
        lines.append("|---|---|")
        for kind in sorted(by_kind):
            lines.append(f"| {kind} | {by_kind[kind]} |")
        lines.append("")
        lines.append("<details><summary>Full anomaly list</summary>")
        lines.append("")
        for a in sorted(anomalies, key=lambda x: (x["kind"], x["file"], x["detail"])):
            lines.append(f"- `{a['kind']}` [{a['file']}] {a['detail']}")
        lines.append("")
        lines.append("</details>")
    lines.append("")

    out_path.write_text("\n".join(lines))


def build_manifest(raw_root: Path) -> tuple[pd.DataFrame, dict[str, int], list[dict]]:
    json_paths = sorted(raw_root.glob("W*-*/output1.json"))
    if not json_paths:
        raise SystemExit(f"No output1.json files found under {raw_root}")

    vocab = build_vocabulary(json_paths)

    anomalies: list[dict] = []
    rows: list[dict] = []
    for path in json_paths:
        rows.extend(parse_output_json(path, anomalies))

    df = pd.DataFrame(rows)
    df["label_idx"] = df["word_id"].map(vocab).astype("int64")
    df["split"] = ""
    df = df[MANIFEST_COLUMNS]

    # Enforce dtypes so the parquet schema is stable and predictable.
    df = df.astype(
        {
            "trial_id": "string",
            "video_path": "string",
            "word_id": "string",
            "label_idx": "int64",
            "signer_id": "string",
            "orientation": "string",
            "session": "string",
            "view": "string",
            "fps": "float64",
            "start_frame": "int64",
            "end_frame": "int64",
            "n_frames": "int64",
            "duration_s": "float64",
            "source": "string",
            "split": "string",
        }
    )
    df = df.sort_values("trial_id", kind="stable").reset_index(drop=True)
    return df, vocab, anomalies


def _print_summary(df: pd.DataFrame, vocab: dict[str, int], anomalies: list[dict]) -> None:
    print("\n=== BdSLW60 manifest ===")
    print(f"{'trials':<22}{len(df)}")
    print(f"{'unique words':<22}{df['word_id'].nunique()}")
    print(f"{'unique signers':<22}{df['signer_id'].nunique()}")
    print(f"{'vocabulary entries':<22}{len(vocab)}")
    print(f"{'anomalies':<22}{len(anomalies)}")
    print(f"{'flagged n_frames':<22}"
          f"{int(((df['n_frames'] < N_FRAMES_MIN) | (df['n_frames'] > N_FRAMES_MAX)).sum())}")
    print("\norientation:")
    print(df["orientation"].value_counts().to_string())
    print("\nfps:")
    print(df["fps"].value_counts().sort_index().to_string())
    print(
        f"\nduration_s: min={df['duration_s'].min():.2f} "
        f"mean={df['duration_s'].mean():.2f} max={df['duration_s'].max():.2f}"
    )
    if anomalies:
        by_kind: dict[str, int] = {}
        for a in anomalies:
            by_kind[a["kind"]] = by_kind.get(a["kind"], 0) + 1
        print("\nanomalies by kind:")
        for kind in sorted(by_kind):
            print(f"  {kind:<24}{by_kind[kind]}")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Build the BdSLW60 trial manifest.")
    ap.add_argument("--raw-root", type=Path, default=repo / "data" / "raw" / "bdslw60")
    ap.add_argument("--manifest", type=Path, default=repo / "data" / "manifest.parquet")
    ap.add_argument("--vocab", type=Path, default=repo / "data" / "vocabulary.json")
    ap.add_argument("--report", type=Path, default=repo / "reports" / "manifest_summary.md")
    args = ap.parse_args()

    df, vocab, anomalies = build_manifest(args.raw_root)

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.manifest, index=False)
    args.vocab.write_text(json.dumps(vocab, indent=2) + "\n")
    write_report(df, anomalies, args.report)

    _print_summary(df, vocab, anomalies)
    print(f"\nwrote {args.manifest}")
    print(f"wrote {args.vocab}")
    print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
