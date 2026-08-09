"""Unit tests for the pure normalize_frame feature builder."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from normalize import FEATURE_DIM, normalize_frame  # noqa: E402


def _pose(l_sh=(1.0, 0.0), r_sh=(0.0, 0.0)):
    # order: nose, L_sh, R_sh, L_elbow, R_elbow, L_wrist, R_wrist
    return np.array([(0.5, -1.0), l_sh, r_sh, (0, 0), (0, 0), (0, 0), (0, 0)], dtype=float)


def test_shape_and_dtype():
    v = normalize_frame([None, None], _pose())
    assert v.shape == (FEATURE_DIM,)
    assert v.dtype == np.float32


def test_missing_hands_are_zeros_with_flags_off():
    v = normalize_frame([None, None], _pose())
    assert np.all(v[0:84] == 0)  # both hand blocks zero
    assert v[98] == 0.0 and v[99] == 0.0


def test_normalization_origin_and_scale():
    # shoulders at (1,0) and (0,0): origin=(0.5,0), scale=1
    hand = np.tile([1.5, 0.0], (21, 1))  # each landmark at (1.5, 0)
    v = normalize_frame([hand, None], _pose())
    # (1.5-0.5)/1 = 1.0 for x, (0-0)/1 = 0 for y
    assert np.allclose(v[0:42:2], 1.0)
    assert np.allclose(v[1:42:2], 0.0)
    assert v[98] == 1.0 and v[99] == 0.0
    # pose R_shoulder (index2) normalized -> x=(0-0.5)/1=-0.5
    assert np.isclose(v[84 + 2 * 2], -0.5)


def test_invalid_when_pose_missing():
    assert np.isnan(normalize_frame([None, None], None)).all()


def test_invalid_when_scale_degenerate():
    v = normalize_frame([None, None], _pose(l_sh=(0.5, 0.5), r_sh=(0.5, 0.5)))
    assert np.isnan(v).all()


def test_hand_b_slot_populates_second_block():
    hand = np.tile([0.5, 0.0], (21, 1))  # at origin -> normalized (0,0)
    v = normalize_frame([None, hand], _pose())
    assert v[98] == 0.0 and v[99] == 1.0
    assert np.all(v[0:42] == 0)  # slot A empty
    assert np.allclose(v[42:84], 0.0)  # slot B normalized to origin
