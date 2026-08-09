"""Unit tests for the pure parsing core of build_manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.build_manifest import build_vocabulary, parse_output_json  # noqa: E402


def _write(tmp_path: Path, folder: str, payload: dict) -> Path:
    d = tmp_path / folder
    d.mkdir()
    (d / "output1.json").write_text(json.dumps(payload))
    return d / "output1.json"


def _entry(fname, session="Day01", view="Front", fps="30", n=2, trials=None):
    return {
        "User": fname.split("W")[0],
        "Orientation": "RightHand",
        "Session": session,
        "View": view,
        "FrameRate": fps,
        "FileName": fname,
        "no_of_trials": str(n),
        "trials": trials or {"0": {"starting": 10, "ending": 60},
                             "1": {"starting": 70, "ending": 130}},
    }


def test_basic_row_shape(tmp_path):
    p = _write(tmp_path, "W11-12", {"W11": {"U1": {"RightHand": {"U1W11F": _entry("U1W11F")}}}})
    (tmp_path / "W11-12" / "U1W11F.mp4").write_bytes(b"x")
    rows = parse_output_json(p)
    assert len(rows) == 2
    r = rows[0]
    assert r["trial_id"] == "U1W11F_t00"
    assert r["video_path"] == "W11-12/U1W11F.mp4"
    assert r["word_id"] == "W11" and r["signer_id"] == "U1"
    assert r["n_frames"] == 50 and r["duration_s"] == pytest.approx(50 / 30)
    assert r["source"] == "bdslw60"
    assert "label_idx" not in r  # assigned globally later


def test_skips_bad_filename(tmp_path):
    p = _write(tmp_path, "W357-358", {"W357": {"U1": {"RightHand": {"x": _entry("U1W357F_1")}}}})
    anomalies: list[dict] = []
    rows = parse_output_json(p, anomalies)
    assert rows == []
    assert any(a["kind"] == "bad_filename" for a in anomalies)


def test_skips_missing_video(tmp_path):
    p = _write(tmp_path, "W11-12", {"W11": {"U1": {"RightHand": {"U1W11F": _entry("U1W11F")}}}})
    anomalies: list[dict] = []
    rows = parse_output_json(p, anomalies)  # no .mp4 written
    assert rows == []
    assert any(a["kind"] == "missing_video" for a in anomalies)


def test_skips_bad_frame_range(tmp_path):
    bad = _entry("U1W11F", trials={"0": {"starting": 100, "ending": 50}})
    p = _write(tmp_path, "W11-12", {"W11": {"U1": {"RightHand": {"U1W11F": bad}}}})
    (tmp_path / "W11-12" / "U1W11F.mp4").write_bytes(b"x")
    anomalies: list[dict] = []
    rows = parse_output_json(p, anomalies)
    assert rows == []
    assert any(a["kind"] == "bad_frame_range" for a in anomalies)


def test_flags_but_keeps_out_of_range_n_frames(tmp_path):
    entry = _entry("U1W11F", trials={"0": {"starting": 0, "ending": 5}})  # 5 frames < 10
    p = _write(tmp_path, "W11-12", {"W11": {"U1": {"RightHand": {"U1W11F": entry}}}})
    (tmp_path / "W11-12" / "U1W11F.mp4").write_bytes(b"x")
    anomalies: list[dict] = []
    rows = parse_output_json(p, anomalies)
    assert len(rows) == 1  # kept
    assert any(a["kind"] == "n_frames_out_of_range" for a in anomalies)


def test_dual_orientation_ids_are_unique(tmp_path):
    left = _entry("U1W11F", trials={"0": {"starting": 10, "ending": 60}})
    left["Orientation"] = "LeftHand"
    right = _entry("U1W11F", trials={"0": {"starting": 200, "ending": 260},
                                     "1": {"starting": 300, "ending": 360}})
    payload = {"W11": {"U1": {"LeftHand": {"a": left}, "RightHand": {"b": right}}}}
    p = _write(tmp_path, "W11-12", payload)
    (tmp_path / "W11-12" / "U1W11F.mp4").write_bytes(b"x")
    rows = parse_output_json(p)
    ids = [r["trial_id"] for r in rows]
    assert ids == ["U1W11F_t00", "U1W11F_t01", "U1W11F_t02"]  # contiguous, unique
    assert len(set(ids)) == len(ids)


def test_no_of_trials_mismatch_logged(tmp_path):
    entry = _entry("U1W11F", n=99)  # declares 99, has 2
    p = _write(tmp_path, "W11-12", {"W11": {"U1": {"RightHand": {"U1W11F": entry}}}})
    (tmp_path / "W11-12" / "U1W11F.mp4").write_bytes(b"x")
    anomalies: list[dict] = []
    parse_output_json(p, anomalies)
    assert any(a["kind"] == "no_of_trials_mismatch" for a in anomalies)


def test_build_vocabulary_sorted_numeric(tmp_path):
    p1 = _write(tmp_path, "W9-10", {"W9": {}, "W10": {}})
    p2 = _write(tmp_path, "W1-2", {"W1": {}, "W2": {}})
    vocab = build_vocabulary([p1, p2])
    assert vocab == {"W1": 0, "W2": 1, "W9": 2, "W10": 3}
