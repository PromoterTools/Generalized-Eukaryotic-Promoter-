#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model architectures and prediction pipeline for the Two-Stage Eukaryotic
Promoter Prediction and Promoter Strength Classification tool.

Stage 1: CNN-BiLSTM with self-attention -> promoter vs non-promoter
Stage 2: species-specific CNN or XGBoost -> strong vs weak promoter
"""

import os
import joblib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from config import config

# =========================================================
# STAGE 1: MODEL DEFINITION
# =========================================================


class MultiScaleCNN(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_sizes, dropout=0.2):
        super().__init__()
        self.convs = nn.ModuleList()
        for k in kernel_sizes:
            padding = k // 2
            self.convs.append(
                nn.Conv1d(in_channels, out_channels // len(kernel_sizes), k, padding=padding)
            )
        self.bn = nn.BatchNorm1d(out_channels)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        conv_outputs = [F.relu(conv(x)) for conv in self.convs]
        x = torch.cat(conv_outputs, dim=1)
        x = self.bn(x)
        x = self.dropout(x)
        return x


class SelfAttention(nn.Module):
    def __init__(self, hidden_size, attention_dim):
        super().__init__()
        self.attention_weights = nn.Linear(hidden_size, attention_dim)
        self.context_vector = nn.Linear(attention_dim, 1, bias=False)

    def forward(self, lstm_outputs, mask=None):
        attention_scores = torch.tanh(self.attention_weights(lstm_outputs))
        attention_scores = self.context_vector(attention_scores).squeeze(-1)
        if mask is not None:
            attention_scores = attention_scores.masked_fill(mask == 0, -1e9)
        attention_weights = F.softmax(attention_scores, dim=1)
        weighted_output = torch.bmm(attention_weights.unsqueeze(1), lstm_outputs).squeeze(1)
        return weighted_output, attention_weights


class CNNBiLSTMClassifier(nn.Module):
    def __init__(
        self,
        vocab_size,
        embedding_dim,
        num_filters,
        kernel_sizes,
        lstm_hidden_size,
        lstm_num_layers,
        attention_dim,
        dropout_rate=0.3,
    ):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        self.cnn_layers = nn.ModuleList()
        in_channels = embedding_dim
        for i, filters in enumerate(num_filters):
            self.cnn_layers.append(MultiScaleCNN(in_channels, filters, kernel_sizes, dropout=0.2))
            if i < len(num_filters) - 1:
                self.cnn_layers.append(nn.MaxPool1d(2))
            in_channels = filters

        self.lstm = nn.LSTM(
            in_channels,
            lstm_hidden_size,
            lstm_num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.3,
        )
        lstm_out = lstm_hidden_size * 2

        self.attention = SelfAttention(lstm_out, attention_dim)

        self.classifier = nn.Sequential(
            nn.Linear(lstm_out, 512), nn.BatchNorm1d(512), nn.ReLU(), nn.Dropout(dropout_rate),
            nn.Linear(512, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(dropout_rate),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(dropout_rate),
            nn.Linear(128, 1), nn.Sigmoid(),
        )

    def forward(self, input_ids, attention_mask):
        x = self.embedding(input_ids)
        x = x.permute(0, 2, 1)

        for layer in self.cnn_layers:
            x = layer(x)

        x = x.permute(0, 2, 1)
        lstm_out, _ = self.lstm(x)

        if attention_mask.size(1) > lstm_out.size(1):
            stride = attention_mask.size(1) // lstm_out.size(1)
            pooled_mask = attention_mask[:, ::stride][:, : lstm_out.size(1)]
        else:
            pooled_mask = attention_mask[:, : lstm_out.size(1)]

        features, attn_weights = self.attention(lstm_out, pooled_mask)
        output = self.classifier(features).squeeze()
        return output, attn_weights


# =========================================================
# STAGE 2: CNN MODEL
# =========================================================


class PromoterStrengthCNN(nn.Module):
    def __init__(self, input_channels=4, num_classes=1):
        super(PromoterStrengthCNN, self).__init__()

        self.conv1 = nn.Conv1d(input_channels, 16, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm1d(16)
        self.pool1 = nn.MaxPool1d(2)

        self.conv2 = nn.Conv1d(16, 32, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(32)
        self.pool2 = nn.MaxPool1d(2)

        self.conv3 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(64)
        self.pool3 = nn.MaxPool1d(2)

        self.global_pool = nn.AdaptiveAvgPool1d(1)

        self.dropout1 = nn.Dropout(0.3)
        self.dropout2 = nn.Dropout(0.2)

        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)

        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)
        x = self.pool3(x)

        x = self.global_pool(x).squeeze(-1)

        x = self.dropout1(x)
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)

        return torch.sigmoid(x).squeeze()


# =========================================================
# HELPER FUNCTIONS
# =========================================================


def clean_sequence(seq):
    """Uppercase, replace ambiguous N with A, and drop any non-ACGT chars."""
    seq = seq.upper().replace("N", "A")
    return "".join(ch for ch in seq if ch in "ACGT")


def encode_sequence(seq, max_len=300):
    encoded = [config.NT_TO_IDX.get(nt, 0) for nt in seq[:max_len]]
    if len(encoded) < max_len:
        encoded += [0] * (max_len - len(encoded))
    return encoded


def one_hot_encode_stage2(sequence, max_len=300):
    mapping = {"A": 0, "C": 1, "G": 2, "T": 3}
    encoded = np.zeros((4, max_len), dtype=np.float32)
    for i, nt in enumerate(sequence[:max_len]):
        if nt in mapping:
            encoded[mapping[nt], i] = 1.0
    return encoded


def one_hot_encode_flat_xgboost(sequence, max_len=300):
    mapping = {"A": 0, "C": 1, "G": 2, "T": 3}
    encoded = np.zeros(max_len * 4, dtype=np.float32)
    for i, nt in enumerate(sequence[:max_len]):
        if nt in mapping:
            encoded[i * 4 + mapping[nt]] = 1.0
    return encoded


def nucleotide_composition(sequence):
    """Return percentage composition of A, C, G, T for a sequence."""
    seq = sequence.upper()
    total = len(seq) if len(seq) > 0 else 1
    return {nt: 100.0 * seq.count(nt) / total for nt in "ACGT"}


# =========================================================
# STAGE 1: LOAD MODEL
# =========================================================


def load_stage1_model():
    print("Loading Stage 1 model (promoter / non-promoter)...")

    model = CNNBiLSTMClassifier(
        vocab_size=config.VOCAB_SIZE,
        embedding_dim=config.EMBEDDING_DIM,
        num_filters=config.NUM_FILTERS,
        kernel_sizes=config.KERNEL_SIZES,
        lstm_hidden_size=config.LSTM_HIDDEN_SIZE,
        lstm_num_layers=config.LSTM_NUM_LAYERS,
        attention_dim=config.ATTENTION_DIM,
        dropout_rate=config.DROPOUT_RATE,
    ).to(config.DEVICE)

    if not os.path.exists(config.STAGE1_MODEL_PATH):
        raise FileNotFoundError(
            f"Stage 1 model checkpoint not found at {config.STAGE1_MODEL_PATH}. "
            "Update STAGE1_MODEL_PATH in config.py."
        )

    checkpoint = torch.load(config.STAGE1_MODEL_PATH, map_location=config.DEVICE)

    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.eval()
    print("Stage 1 model loaded.")
    return model


def predict_stage1(model, sequence):
    encoded = encode_sequence(sequence, config.MAX_SEQ_LEN)
    input_ids = torch.tensor([encoded], dtype=torch.long).to(config.DEVICE)
    attention_mask = (input_ids != 0).float()

    with torch.no_grad():
        output, _ = model(input_ids, attention_mask)
        if output.dim() == 0:
            probability = output.item()
        else:
            probability = output.cpu().numpy()[0]

    return float(probability)


# =========================================================
# STAGE 2: LOAD SPECIES MODELS
# =========================================================

_model_cache = {}


def load_stage2_model(species):
    if species in _model_cache:
        return _model_cache[species]

    if species not in config.STAGE2_MODELS:
        return None, None, None

    model_info = config.STAGE2_MODELS[species]
    model_type = model_info["type"]
    model_path = model_info["path"]
    scaler_path = model_info.get("scaler")

    if not os.path.exists(model_path):
        return None, None, None

    if model_type == "cnn":
        model = PromoterStrengthCNN(input_channels=4, num_classes=1).to(config.DEVICE)
        model.load_state_dict(torch.load(model_path, map_location=config.DEVICE))
        model.eval()
        scaler = None
        print(f"{species} CNN model loaded.")

    elif model_type == "xgboost":
        model = joblib.load(model_path)
        if scaler_path and os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
        else:
            scaler = None
        print(f"{species} XGBoost model loaded.")

    else:
        return None, None, None

    _model_cache[species] = (model, model_type, scaler)
    return model, model_type, scaler


def predict_stage2_cnn(model, sequence):
    encoded = one_hot_encode_stage2(sequence, config.MAX_SEQ_LEN)
    input_tensor = torch.tensor([encoded], dtype=torch.float).to(config.DEVICE)

    with torch.no_grad():
        output = model(input_tensor)
        probability = output.item()

    return probability


def predict_stage2_xgboost(model, sequence, scaler=None):
    encoded = one_hot_encode_flat_xgboost(sequence, config.MAX_SEQ_LEN)

    if scaler is not None:
        encoded = scaler.transform([encoded])[0]

    probability = model.predict_proba([encoded])[0][1]

    return probability


# =========================================================
# MAIN PIPELINE
# =========================================================


def predict_promoter_pipeline(sequence, stage1_model, stage1_threshold=0.5):
    """
    Complete two-stage pipeline for one sequence.
    Returns: (results_dict, best_species_name)
    """
    sequence = clean_sequence(sequence)

    results = {
        "sequence": sequence,
        "is_promoter": False,
        "promoter_probability": 0.0,
        "species": None,
        "strength": None,
        "strength_probability": 0.0,
        "message": "",
        "all_species_predictions": {},
        "composition": nucleotide_composition(sequence),
    }

    if len(sequence) == 0:
        results["message"] = "Empty or invalid sequence (no valid A/C/G/T bases found)."
        return results, None

    # Stage 1: promoter prediction
    promoter_prob = predict_stage1(stage1_model, sequence)
    results["promoter_probability"] = promoter_prob

    if promoter_prob < stage1_threshold:
        results["is_promoter"] = False
        results["message"] = f"Non-promoter (probability: {promoter_prob:.4f})"
        return results, None

    results["is_promoter"] = True
    results["message"] = f"Promoter detected (probability: {promoter_prob:.4f})"

    # Stage 2: try all species models, keep the best match
    best_strength_prob = -1
    best_species = None
    best_strength = None
    all_predictions = {}

    for species in config.STAGE2_MODELS.keys():
        model, model_type, scaler = load_stage2_model(species)

        if model is None:
            continue

        try:
            if model_type == "cnn":
                strength_prob = predict_stage2_cnn(model, sequence)
            else:
                strength_prob = predict_stage2_xgboost(model, sequence, scaler)

            strength_label = "Strong" if strength_prob >= 0.5 else "Weak"
            all_predictions[species] = {
                "probability": strength_prob,
                "strength": strength_label,
            }

            if strength_prob > best_strength_prob:
                best_strength_prob = strength_prob
                best_species = species
                best_strength = strength_label

        except Exception as e:
            print(f"Warning: error predicting for {species}: {e}")
            continue

    results["all_species_predictions"] = all_predictions

    if best_species is not None:
        if best_strength_prob >= config.SPECIES_CONFIDENCE_THRESHOLD:
            results["species"] = best_species
            results["strength"] = best_strength
            results["strength_probability"] = best_strength_prob
            results["message"] += (
                f" | Classified as {best_strength} promoter in {best_species} "
                f"(prob: {best_strength_prob:.4f})"
            )
        else:
            results["species"] = "Unknown"
            results["strength"] = best_strength
            results["strength_probability"] = best_strength_prob
            results["message"] += (
                f" | Best match: {best_strength} promoter in {best_species} "
                f"(prob: {best_strength_prob:.4f}) - below confidence threshold, "
                f"classified as Unknown species"
            )
    else:
        results["message"] += " | Could not determine species-specific strength"

    return results, best_species
