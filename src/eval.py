"""Evaluate models/best.pt on val AND heldout (Spec 03).

Writes reports/eval_{split}.json (overall top-1/top-5, per-class P/R/F1/support,
per-signer top-1, confusion matrix, macro-F1) and a human-readable
reports/eval_summary.md with tables and the 10 most confused class pairs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from torch.utils.data import DataLoader

from config import REPO, load_params, load_vocabulary
from dataset import LandmarkDataset
from model import build_model


@torch.no_grad()
def run_split(model, params, split, device, topk):
    ds = LandmarkDataset(params, split, augment=False)
    loader = DataLoader(ds, batch_size=params["train"]["batch_size"], shuffle=False)

    all_labels, all_preds, all_top5, all_signers = [], [], [], []
    for feats, labels, signers in loader:
        logits = model(feats.to(device))
        top5 = logits.topk(topk, dim=1).indices.cpu().numpy()
        all_top5.append(top5)
        all_preds.append(logits.argmax(1).cpu().numpy())
        all_labels.append(labels.numpy())
        all_signers.extend(signers)

    labels = np.concatenate(all_labels)
    preds = np.concatenate(all_preds)
    top5 = np.concatenate(all_top5)
    return ds, labels, preds, top5, all_signers


def build_report(labels, preds, top5, signers, num_classes, inv_vocab):
    top1 = float((preds == labels).mean())
    top5_acc = float(np.mean([lbl in row for lbl, row in zip(labels, top5)]))

    class_ids = list(range(num_classes))
    prec, rec, f1, support = precision_recall_fscore_support(
        labels, preds, labels=class_ids, zero_division=0)
    per_class = [
        {
            "label_idx": c,
            "word_id": inv_vocab[c],
            "precision": float(prec[c]),
            "recall": float(rec[c]),
            "f1": float(f1[c]),
            "support": int(support[c]),
        }
        for c in class_ids
    ]
    macro_f1 = float(f1_score(labels, preds, labels=class_ids, average="macro", zero_division=0))

    per_signer = {}
    by_signer_correct = defaultdict(int)
    by_signer_total = defaultdict(int)
    for lbl, pred, sig in zip(labels, preds, signers):
        by_signer_total[sig] += 1
        by_signer_correct[sig] += int(pred == lbl)
    for sig in sorted(by_signer_total, key=lambda s: int(s[1:])):
        per_signer[sig] = {
            "top1": by_signer_correct[sig] / by_signer_total[sig],
            "support": by_signer_total[sig],
        }

    cm = confusion_matrix(labels, preds, labels=class_ids)
    return {
        "n_samples": int(len(labels)),
        "overall_top1": top1,
        "overall_top5": top5_acc,
        "macro_f1": macro_f1,
        "per_class": per_class,
        "per_signer_top1": per_signer,
        "confusion_matrix": cm.tolist(),
    }


def most_confused_pairs(cm, inv_vocab, k):
    cm = np.asarray(cm)
    pairs = {}
    n = cm.shape[0]
    for i in range(n):
        for j in range(n):
            if i == j or cm[i, j] == 0:
                continue
            key = tuple(sorted((i, j)))
            pairs[key] = pairs.get(key, 0) + int(cm[i, j])
    ranked = sorted(pairs.items(), key=lambda kv: kv[1], reverse=True)[:k]
    return [(inv_vocab[a], inv_vocab[b], cnt) for (a, b), cnt in ranked]


def write_summary(reports: dict, inv_vocab, k_pairs, out_path):
    lines = ["# BdSLW60 evaluation summary", ""]
    for split, rep in reports.items():
        lines += [f"## {split}", "",
                  f"- samples: {rep['n_samples']}",
                  f"- top-1: **{rep['overall_top1']:.4f}**",
                  f"- top-5: **{rep['overall_top5']:.4f}**",
                  f"- macro-F1: **{rep['macro_f1']:.4f}**", ""]

        lines += ["### Per-signer top-1 (key metric)", "",
                  "| signer | top-1 | support |", "|---|---|---|"]
        for sig, v in rep["per_signer_top1"].items():
            lines.append(f"| {sig} | {v['top1']:.4f} | {v['support']} |")
        lines.append("")

        pairs = most_confused_pairs(rep["confusion_matrix"], inv_vocab, k_pairs)
        lines += [f"### Top {k_pairs} most confused class pairs", "",
                  "| word A | word B | count |", "|---|---|---|"]
        for a, b, cnt in pairs:
            lines.append(f"| {a} | {b} | {cnt} |")
        lines.append("")

        worst = sorted(rep["per_class"], key=lambda r: r["f1"])[:10]
        lines += ["### 10 lowest-F1 classes", "",
                  "| word | precision | recall | f1 | support |", "|---|---|---|---|---|"]
        for r in worst:
            lines.append(f"| {r['word_id']} | {r['precision']:.3f} | {r['recall']:.3f} "
                         f"| {r['f1']:.3f} | {r['support']} |")
        lines.append("")

    out_path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate best checkpoint on val + heldout.")
    ap.add_argument("--params", type=Path, default=REPO / "configs" / "params.yaml")
    args = ap.parse_args()

    params = load_params(args.params)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    vocab = load_vocabulary(REPO / params["data"]["vocabulary"])
    inv_vocab = {idx: word for word, idx in vocab.items()}
    num_classes = params["model"]["num_classes"]

    ckpt = torch.load(REPO / params["paths"]["best_ckpt"], map_location=device, weights_only=False)
    model = build_model(params).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"loaded checkpoint (epoch {ckpt['epoch']}, val_top1 {ckpt['val_top1']:.4f})")

    eval_dir = REPO / params["paths"]["eval_dir"]
    eval_dir.mkdir(parents=True, exist_ok=True)

    reports = {}
    for split in ("val", "heldout"):
        _ds, labels, preds, top5, signers = run_split(
            model, params, split, device, params["eval"]["topk"])
        rep = build_report(labels, preds, top5, signers, num_classes, inv_vocab)
        reports[split] = rep
        (eval_dir / f"eval_{split}.json").write_text(json.dumps(rep, indent=2))
        print(f"{split:8} top1 {rep['overall_top1']:.4f} top5 {rep['overall_top5']:.4f} "
              f"macroF1 {rep['macro_f1']:.4f} -> reports/eval_{split}.json")

    write_summary(reports, inv_vocab, params["eval"]["confused_pairs"], eval_dir / "eval_summary.md")
    print(f"wrote {eval_dir / 'eval_summary.md'}")


if __name__ == "__main__":
    main()
