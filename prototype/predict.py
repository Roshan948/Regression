"""
predict.py — loads the saved checkpoint and exposes predict(data: dict) -> int,
the same interface as the reference project's predict.py.

Fix vs. reference: the reference's predict.py hardcodes a BikeNN architecture
(64 -> 32 -> 16) that does not match either the shape its own README
describes (128 -> 64 -> 32) or necessarily the shape Optuna actually picked.
Here, the hidden layer sizes are read back from the checkpoint itself
(saved by the notebook right after training), so the reconstructed network
always matches the trained weights exactly.
"""
import os
import math

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class BikeNN(torch.nn.Module):
    def __init__(self, n, hidden_sizes=(64, 32, 16)):
        super().__init__()
        layers = []
        prev = n
        for h in hidden_sizes:
            layers += [torch.nn.Linear(prev, h), torch.nn.ReLU()]
            prev = h
        layers.append(torch.nn.Linear(prev, 1))
        self.net = torch.nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


checkpoint = torch.load(
    os.path.join(BASE_DIR, "..", "model", "bike_model.pt"),
    map_location=device, weights_only=False,
)

model = BikeNN(checkpoint["n_features"], tuple(checkpoint["hidden_sizes"])).to(device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

feature_names = checkpoint["feature_names"]
numeric_cols = checkpoint["numeric_cols"]

scaler = StandardScaler()
scaler.mean_ = checkpoint["scaler_mean"]
scaler.scale_ = checkpoint["scaler_scale"]
scaler.n_features_in_ = len(numeric_cols)
scaler.feature_names_in_ = np.array(numeric_cols, dtype=object)


def predict(data: dict) -> int:
    """
    data must contain: year, month, day, hour, temp, humidity, windspeed,
    holiday (0/1), workingday (0/1), and one-hot flags weather_1..weather_4,
    season_1..season_4 (exactly as the training notebook builds them).
    """
    row = pd.DataFrame([data])[feature_names].copy()
    row[numeric_cols] = scaler.transform(row[numeric_cols])
    x_t = torch.tensor(row.to_numpy(dtype=np.float32), dtype=torch.float32).to(device)

    with torch.no_grad():
        pred_log = model(x_t)

    pred = np.expm1(pred_log.cpu().numpy())
    return math.ceil(max(pred.flatten()[0], 0))
