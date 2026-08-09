"""Load configs/params.yaml into a plain dict and provide seeding helpers.

Keeping this tiny and dependency-light so train/eval/export all share one source
of truth for hyperparameters (no magic numbers anywhere else).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PARAMS = REPO / "configs" / "params.yaml"


def load_params(path: Path | str = DEFAULT_PARAMS) -> dict:
    return yaml.safe_load(Path(path).read_text())


def load_vocabulary(path: Path | str) -> dict[str, int]:
    return json.loads(Path(path).read_text())


def seed_everything(seed: int) -> None:
    """Seed python/numpy/torch. Returns nothing; caller logs determinism caveats."""
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # Deterministic cuDNN so repeated runs land within tolerance. NOTE: cuDNN LSTM
    # kernels are only *approximately* reproducible on GPU even with this set —
    # small run-to-run drift in val top-1 is expected (see acceptance's 0.5% band).
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
