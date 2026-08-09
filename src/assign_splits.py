"""Part A — assign the ``split`` column in the manifest from configs/splits.yaml.

Splits are signer-disjoint and hand-written (never derived). Trials failing the
duration-quality gate are marked ``excluded`` and will not be extracted.

Exclusion rule (a trial is excluded if either holds):
    * n_frames < 8
    * n_frames < 0.4 * (median n_frames for that word_id)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

MIN_FRAMES = 8
REL_MEDIAN_FLOOR = 0.4


def load_split_map(splits_path: Path) -> dict[str, str]:
    """Return {signer_id: split_name} from a splits.yaml of {split: [signers]}."""
    cfg = yaml.safe_load(splits_path.read_text())
    signer_to_split: dict[str, str] = {}
    for split_name, signers in cfg.items():
        for signer in signers:
            if signer in signer_to_split:
                raise ValueError(f"signer {signer} listed in multiple splits")
            signer_to_split[signer] = split_name
    return signer_to_split


def assign_splits(df: pd.DataFrame, signer_to_split: dict[str, str]) -> pd.Series:
    """Compute the split label for every row (does not mutate ``df``)."""
    word_median = df.groupby("word_id")["n_frames"].transform("median")
    excluded = (df["n_frames"] < MIN_FRAMES) | (
        df["n_frames"] < REL_MEDIAN_FLOOR * word_median
    )

    missing = set(df.loc[~excluded, "signer_id"]) - set(signer_to_split)
    if missing:
        raise ValueError(f"signers with no split assignment: {sorted(missing)}")

    split = df["signer_id"].map(signer_to_split)
    split = split.where(~excluded, "excluded")
    return split.astype("string")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Assign manifest split column.")
    ap.add_argument("--manifest", type=Path, default=repo / "data" / "manifest.parquet")
    ap.add_argument("--splits", type=Path, default=repo / "configs" / "splits.yaml")
    args = ap.parse_args()

    df = pd.read_parquet(args.manifest)
    signer_to_split = load_split_map(args.splits)
    df["split"] = assign_splits(df, signer_to_split)
    df.to_parquet(args.manifest, index=False)

    print("split assignment:")
    print(df["split"].value_counts().to_string())
    print(f"\ntotal {len(df)}, to-extract {int((df['split'] != 'excluded').sum())}")


if __name__ == "__main__":
    main()
