"""Baseline sign classifier: 2-layer BiLSTM + attention pooling.

    input (B, 48, 200)
      -> BiLSTM(hidden per direction, num_layers, dropout between layers)  (B, 48, 2*hidden)
      -> attention pooling over time (single learned query)                (B, 2*hidden)
      -> linear                                                            (B, num_classes)
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn


class AttentionPool(nn.Module):
    """Single-head attention pooling with a learned query vector."""

    def __init__(self, dim: int):
        super().__init__()
        self.query = nn.Parameter(torch.randn(dim))
        self.scale = 1.0 / math.sqrt(dim)

    def forward(self, h: torch.Tensor) -> torch.Tensor:  # h: (B, T, dim)
        scores = (h @ self.query) * self.scale           # (B, T)
        weights = torch.softmax(scores, dim=1)            # (B, T)
        return torch.einsum("bt,btd->bd", weights, h)     # (B, dim)


class SignClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden: int, num_layers: int,
                 dropout: float, num_classes: int):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout,
        )
        self.attn = AttentionPool(2 * hidden)
        self.head = nn.Linear(2 * hidden, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # x: (B, T, input_dim)
        h, _ = self.lstm(x)
        pooled = self.attn(h)
        return self.head(pooled)


def build_model(params: dict) -> SignClassifier:
    m = params["model"]
    return SignClassifier(
        input_dim=m["input_dim"],
        hidden=m["hidden"],
        num_layers=m["num_layers"],
        dropout=m["dropout"],
        num_classes=m["num_classes"],
    )


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
