"""Train the baseline sign classifier (Spec 03).

Adam + cosine LR decay, label smoothing, grad clip, early stop on val top-1,
best checkpoint to models/best.pt, everything logged to a local MLflow store.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# MLflow 3.x gates the local file store; the spec mandates a local mlruns/ backend.
os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

import mlflow
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from config import REPO, load_params, seed_everything
from dataset import LandmarkDataset
from model import build_model, count_parameters


def _loader(ds, batch_size, shuffle, num_workers, generator=None):
    return DataLoader(
        ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
        drop_last=False, generator=generator,
    )


@torch.no_grad()
def evaluate(model, loader, device, criterion) -> tuple[float, float]:
    model.eval()
    loss_sum, correct, total = 0.0, 0, 0
    for feats, labels, _signers in loader:
        feats, labels = feats.to(device), labels.to(device)
        logits = model(feats)
        loss_sum += criterion(logits, labels).item() * labels.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return loss_sum / total, correct / total


def train_one_epoch(model, loader, device, criterion, optimizer, grad_clip) -> tuple[float, float]:
    model.train()
    loss_sum, correct, total = 0.0, 0, 0
    for feats, labels, _signers in loader:
        feats, labels = feats.to(device), labels.to(device)
        optimizer.zero_grad()
        logits = model(feats)
        loss = criterion(logits, labels)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()
        loss_sum += loss.item() * labels.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return loss_sum / total, correct / total


def main() -> None:
    ap = argparse.ArgumentParser(description="Train baseline sign classifier.")
    ap.add_argument("--params", type=Path, default=REPO / "configs" / "params.yaml")
    ap.add_argument("--max-epochs", type=int, default=None, help="override for smoke tests")
    args = ap.parse_args()

    params = load_params(args.params)
    tp = params["train"]
    seed = params["seed"]
    seed_everything(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    max_epochs = args.max_epochs if args.max_epochs is not None else tp["max_epochs"]

    gen = torch.Generator().manual_seed(seed)
    train_ds = LandmarkDataset(params, "train", augment=True)
    val_ds = LandmarkDataset(params, "val", augment=False)
    train_loader = _loader(train_ds, tp["batch_size"], True, tp["num_workers"], gen)
    val_loader = _loader(val_ds, tp["batch_size"], False, tp["num_workers"])

    model = build_model(params).to(device)
    n_params = count_parameters(model)
    print(f"model parameters: {n_params:,}")
    print(f"device: {device} | train {len(train_ds)} | val {len(val_ds)} | epochs {max_epochs}")

    criterion = nn.CrossEntropyLoss(label_smoothing=tp["label_smoothing"])
    optimizer = torch.optim.Adam(model.parameters(), lr=tp["lr"], weight_decay=tp["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=max_epochs, eta_min=tp["lr_min"])

    ckpt_path = REPO / params["paths"]["best_ckpt"]
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri((REPO / params["paths"]["mlruns"]).as_uri())
    mlflow.set_experiment(tp["experiment"])

    best_val_top1, best_epoch, epochs_no_improve = 0.0, -1, 0
    with mlflow.start_run():
        mlflow.log_params({
            "seed": seed, "param_count": n_params, "max_epochs": max_epochs,
            **{f"model.{k}": v for k, v in params["model"].items()},
            **{f"train.{k}": v for k, v in tp.items()},
            **{f"augment.{k}": v for k, v in params["augment"].items()},
            "train_samples": len(train_ds), "val_samples": len(val_ds),
        })

        for epoch in range(max_epochs):
            tr_loss, tr_top1 = train_one_epoch(
                model, train_loader, device, criterion, optimizer, tp["grad_clip"])
            val_loss, val_top1 = evaluate(model, val_loader, device, criterion)
            scheduler.step()

            if tr_loss != tr_loss:  # NaN guard
                raise RuntimeError(f"NaN train loss at epoch {epoch}")

            mlflow.log_metrics({
                "train_loss": tr_loss, "train_top1": tr_top1,
                "val_loss": val_loss, "val_top1": val_top1,
                "lr": scheduler.get_last_lr()[0],
            }, step=epoch)

            improved = val_top1 > best_val_top1
            marker = ""
            if improved:
                best_val_top1, best_epoch, epochs_no_improve = val_top1, epoch, 0
                torch.save({
                    "model_state": model.state_dict(),
                    "params": params, "epoch": epoch, "val_top1": val_top1,
                }, ckpt_path)
                marker = " *"
            else:
                epochs_no_improve += 1

            print(f"epoch {epoch:3d} | train loss {tr_loss:.4f} top1 {tr_top1:.4f} "
                  f"| val loss {val_loss:.4f} top1 {val_top1:.4f}{marker}")

            if epochs_no_improve >= tp["patience"]:
                print(f"early stop at epoch {epoch} (no val improvement for {tp['patience']})")
                break

        mlflow.log_metric("best_val_top1", best_val_top1)
        mlflow.log_param("best_epoch", best_epoch)

    print(f"\nbest val top-1: {best_val_top1:.4f} @ epoch {best_epoch}")
    print(f"saved best checkpoint -> {ckpt_path}")


if __name__ == "__main__":
    main()
