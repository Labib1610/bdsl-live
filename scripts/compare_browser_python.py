"""Run the trained model over the stored U2W37F_t* npz files and print predictions.

A reference for cross-checking the browser app: it feeds the same stored
(48, 100) landmark features through the identical first-diff + model path the
browser reproduces in JS, so the top-k here is what the app should output for
these clips.
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(REPO / "src"))

from config import load_params, load_vocabulary  # noqa: E402
from model import build_model  # noqa: E402

PREFIX = "U2W37F_t"


def build_features(coords: np.ndarray) -> np.ndarray:
    """(48,100) coords -> (48,200) coords+first-diff, matching src/dataset.py."""
    diff = np.zeros_like(coords)
    diff[1:] = coords[1:] - coords[:-1]
    return np.concatenate([coords, diff], axis=1).astype(np.float32)


def main() -> None:
    ap = argparse.ArgumentParser(description="Predict on U2W37F_t* npz with the trained model.")
    ap.add_argument("--params", type=Path, default=REPO / "configs" / "params.yaml")
    ap.add_argument("--split", default="val", help="landmarks split dir holding the files")
    ap.add_argument("--topk", type=int, default=3)
    args = ap.parse_args()

    params = load_params(args.params)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    vocab = load_vocabulary(REPO / params["data"]["vocabulary"])
    inv_vocab = {idx: word for word, idx in vocab.items()}

    ckpt = torch.load(REPO / params["paths"]["best_ckpt"], map_location=device, weights_only=False)
    model = build_model(params).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"checkpoint: epoch {ckpt['epoch']}, val_top1 {ckpt['val_top1']:.4f}")

    files = sorted(glob.glob(str(REPO / "data" / "landmarks" / args.split / f"{PREFIX}*.npz")))
    if not files:
        raise SystemExit(f"no {PREFIX}* files under split '{args.split}'")

    correct = 0
    print(f"\n{'trial':16} {'true':6} {'presence':8} top-{args.topk} predictions")
    print("-" * 70)
    for f in files:
        z = np.load(f, allow_pickle=False)
        coords = z["features"].astype(np.float32)
        true_word = str(z["word_id"])
        presence = float(z["hand_presence_rate"])

        feats = torch.from_numpy(build_features(coords)).unsqueeze(0).to(device)
        with torch.no_grad():
            probs = torch.softmax(model(feats), dim=1)[0]
        conf, idx = probs.topk(args.topk)
        preds = [f"{inv_vocab[int(i)]} {float(c) * 100:5.1f}%" for c, i in zip(conf, idx)]

        hit = inv_vocab[int(idx[0])] == true_word
        correct += hit
        mark = "OK " if hit else "  x"
        print(f"{Path(f).stem:16} {true_word:6} {presence:8.3f} {mark} " + " | ".join(preds))

    print("-" * 70)
    print(f"top-1 accuracy on {PREFIX}*: {correct}/{len(files)} = {correct / len(files):.3f}")


if __name__ == "__main__":
    main()
