# Spec 03 — Baseline model + training

## Goal
Train a sign classifier on the extracted landmarks. Report overall and
per-signer accuracy. Export ONNX.

## Data loading (`src/dataset.py`)
- Reads npz files from `data/landmarks/{split}/`
- Filter: drop samples with `hand_presence_rate < 0.3` from **train and val only**.
  Keep all heldout samples.
- Input features per sample, computed in the loader (not stored):
  - raw normalized coords: (48, 100)
  - first differences along time, zero-padded at t=0: (48, 100)
  - concatenated → **(48, 200)**
- Label from `vocabulary.json`.
- Return `(features, label_idx, signer_id)`.

### Augmentation (train split only)
- random time shift ±3 frames (roll, edge-pad)
- gaussian noise σ=0.01 on coordinates
- random scale 0.95–1.05
- random rotation ±10° in the xy plane
Each applied with p=0.5, independently. No augmentation on val/heldout.

## Model (`src/model.py`)
2-layer bidirectional LSTM:
- input 200 → hidden 256 per direction
- dropout 0.3 between layers
- attention pooling over time (learned query, single head) → 512
- linear 512 → 60
Report parameter count.

## Training (`src/train.py`)
- Adam, lr 1e-3, cosine decay to 1e-5
- batch 64, max 100 epochs
- label smoothing 0.1
- early stop on val top-1, patience 15
- grad clip 1.0
- seed from params.yaml, set for torch/numpy/random; log determinism caveats
- checkpoint best val to `models/best.pt`
- log to MLflow (local `mlruns/`): all params, per-epoch train/val loss + top-1

All hyperparameters live in `configs/params.yaml`. No magic numbers in code.

## Evaluation (`src/eval.py`)
Loads `models/best.pt`, evaluates on val AND heldout separately.
Emits `reports/eval_{split}.json`:
- overall top-1, top-5
- per-class precision/recall/F1/support
- **per-signer top-1** (the key metric)
- confusion matrix as nested list
- macro-F1

Also `reports/eval_summary.md` — human-readable tables, plus the 10 most
confused class pairs.

## ONNX export (`src/export_onnx.py`)
- opset 17, dynamic batch axis, input `(B, 48, 200)`
- parity check: 20 random samples, torch vs onnxruntime, assert max abs diff < 1e-4
- write to `models/model.onnx`, print size

## Acceptance
- training completes without NaN loss
- val top-1 > 0.40 (sanity floor; chance is 1.7%)
- eval JSONs contain all listed keys
- ONNX parity passes
- rerunning train with the same seed reproduces val top-1 within 0.5%