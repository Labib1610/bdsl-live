"""Export models/best.pt to ONNX with a dynamic batch axis and check parity.

opset 17, input `features` (B, 48, 200) -> output `logits` (B, 60). Verifies
torch vs onnxruntime agree to < parity_tol on random samples.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch

from config import REPO, load_params
from dataset import LandmarkDataset
from model import build_model


def main() -> None:
    ap = argparse.ArgumentParser(description="Export baseline model to ONNX + parity check.")
    ap.add_argument("--params", type=Path, default=REPO / "configs" / "params.yaml")
    args = ap.parse_args()

    params = load_params(args.params)
    n_frames = params["features"]["n_frames"]
    input_dim = params["features"]["input_dim"]
    onnx_cfg = params["onnx"]

    # Export on CPU for a portable graph and apples-to-apples parity.
    ckpt = torch.load(REPO / params["paths"]["best_ckpt"], map_location="cpu", weights_only=False)
    model = build_model(params)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    onnx_path = REPO / params["paths"]["onnx"]
    onnx_path.parent.mkdir(parents=True, exist_ok=True)

    dummy = torch.randn(1, n_frames, input_dim)
    torch.onnx.export(
        model, dummy, str(onnx_path),
        input_names=["features"], output_names=["logits"],
        dynamic_axes={"features": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=onnx_cfg["opset"], dynamo=False,
    )
    size_mb = onnx_path.stat().st_size / 1e6
    print(f"exported {onnx_path} ({size_mb:.2f} MB, opset {onnx_cfg['opset']})")

    # Parity: N random val samples through torch vs onnxruntime.
    ds = LandmarkDataset(params, "val", augment=False)
    n = min(onnx_cfg["parity_samples"], len(ds))
    rng = np.random.default_rng(params["seed"])
    idxs = rng.choice(len(ds), size=n, replace=False)
    batch = torch.stack([ds[int(i)][0] for i in idxs])  # (n, 48, 200)

    with torch.no_grad():
        torch_out = model(batch).numpy()
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    onnx_out = sess.run(["logits"], {"features": batch.numpy()})[0]

    max_diff = float(np.max(np.abs(torch_out - onnx_out)))
    tol = onnx_cfg["parity_tol"]
    print(f"parity: {n} samples, max abs diff {max_diff:.2e} (tol {tol:.1e})")
    assert max_diff < tol, f"ONNX parity failed: {max_diff} >= {tol}"
    print("ONNX parity OK")


if __name__ == "__main__":
    main()
