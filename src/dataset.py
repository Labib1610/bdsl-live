"""Landmark dataset: reads per-trial npz, builds (48, 200) features in-loader.

Feature construction (per sample, computed here — never stored):
    coords : (48, 100)  raw normalized landmarks (incl. 2 presence flags)
    diff   : (48, 100)  first difference along time, zero-padded at t=0
    -> concat on channel axis -> (48, 200)

Train-split augmentation (each applied independently with prob p) acts on the
coordinate channels only (0..97); presence flags are never perturbed, and
absent-hand blocks are re-zeroed afterwards to preserve the "missing = zeros"
invariant. Augmentation happens before the diff is computed.
"""

from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from config import REPO, load_vocabulary

# Feature layout constants (mirror src/normalize.py).
HAND_A = slice(0, 42)
HAND_B = slice(42, 84)
FLAG_A, FLAG_B = 98, 99


class LandmarkDataset(Dataset):
    def __init__(self, params: dict, split: str, augment: bool = False):
        self.params = params
        self.split = split
        self.augment = augment
        self.aug = params["augment"]
        self.n_coord = params["features"]["n_coord_channels"]  # 98

        vocab = load_vocabulary(REPO / params["data"]["vocabulary"])
        root = REPO / params["data"]["landmarks_dir"] / split
        files = sorted(glob.glob(str(root / "*.npz")))

        min_rate = params["data"]["min_hand_presence_rate"]
        drop_low = split in ("train", "val")  # keep all heldout

        self.coords: list[np.ndarray] = []
        self.labels: list[int] = []
        self.signers: list[str] = []
        for f in files:
            z = np.load(f, allow_pickle=False)
            if drop_low and float(z["hand_presence_rate"]) < min_rate:
                continue
            self.coords.append(z["features"].astype(np.float32))  # (48, 100)
            self.labels.append(int(vocab[str(z["word_id"])]))
            self.signers.append(str(z["signer_id"]))

        if not self.coords:
            raise RuntimeError(f"no samples found for split={split} under {root}")

    def __len__(self) -> int:
        return len(self.coords)

    # ---- augmentation helpers (operate on a (48, 100) coord array copy) ----
    def _augment(self, coords: np.ndarray) -> np.ndarray:
        a = self.aug
        p = a["prob"]
        n = self.n_coord
        flags = coords[:, FLAG_A:FLAG_B + 1].copy()

        # 1. random time shift (+/- k frames) with edge padding
        if np.random.rand() < p and a["time_shift"] > 0:
            k = np.random.randint(-a["time_shift"], a["time_shift"] + 1)
            if k != 0:
                coords = np.roll(coords, k, axis=0)
                if k > 0:
                    coords[:k] = coords[k]      # edge-pad the exposed head
                else:
                    coords[k:] = coords[k - 1]  # edge-pad the exposed tail

        # 2. gaussian noise on coordinates
        if np.random.rand() < p and a["noise_sigma"] > 0:
            coords[:, :n] += np.random.normal(0.0, a["noise_sigma"], size=coords[:, :n].shape).astype(np.float32)

        # 3. isotropic scale
        if np.random.rand() < p:
            s = np.random.uniform(a["scale_min"], a["scale_max"])
            coords[:, :n] *= np.float32(s)

        # 4. rotation in xy plane
        if np.random.rand() < p and a["rotation_deg"] > 0:
            theta = np.deg2rad(np.random.uniform(-a["rotation_deg"], a["rotation_deg"]))
            c, sn = np.cos(theta), np.sin(theta)
            xy = coords[:, :n].reshape(coords.shape[0], n // 2, 2)
            x, y = xy[..., 0].copy(), xy[..., 1].copy()
            xy[..., 0] = x * c - y * sn
            xy[..., 1] = x * sn + y * c
            coords[:, :n] = xy.reshape(coords.shape[0], n)

        # restore flags; re-zero absent hands so augmentation can't leak into them
        coords[:, FLAG_A:FLAG_B + 1] = flags
        coords[flags[:, 0] <= 0.5, HAND_A] = 0.0
        coords[flags[:, 1] <= 0.5, HAND_B] = 0.0
        return coords

    def __getitem__(self, idx: int):
        coords = self.coords[idx].copy()
        if self.augment:
            coords = self._augment(coords)

        diff = np.zeros_like(coords)
        diff[1:] = coords[1:] - coords[:-1]
        feats = np.concatenate([coords, diff], axis=1)  # (48, 200)

        return torch.from_numpy(feats), self.labels[idx], self.signers[idx]
