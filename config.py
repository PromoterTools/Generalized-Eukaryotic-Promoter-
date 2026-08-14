#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for the Two-Stage Eukaryotic Promoter Prediction Flask app.

Stage 1: Promoter vs Non-promoter (CNN-BiLSTM, shared across species)
Stage 2: Strong vs Weak (species-specific CNN or XGBoost models)

Update the paths below to point at your trained model checkpoints.
"""

import os
import torch


class Config:
    # ---------------------------------------------------------------
    # Stage 1 model
    # ---------------------------------------------------------------
    STAGE1_MODEL_PATH = "D:/chen Promoter work/web_server/noHUb_Promoter_CNN_BiLSTM_300bp_Model_Complete_26_May_2/saved_models/best_model.pth"

    # ---------------------------------------------------------------
    # Stage 2 models, one entry per species
    # ---------------------------------------------------------------
    STAGE2_MODELS = {
        "Human": {
            "type": "cnn",
            "path": "D:/chen Promoter work/web_server/S2_models_July_Human/model_weights.pth",
            "scaler": None,
        },
        "Mouse": {
            "type": "xgboost",
            "path": "D:/chen Promoter work/web_server/S2_XGBoost_Mouse/xgboost_model.pkl",
            "scaler": "D:/chen Promoter work/web_server/S2_XGBoost_Mouse/scaler.pkl",
        },
        "Rat": {
            "type": "cnn",
            "path": "D:/chen Promoter work/web_server/S2_models_July_RAT/model_weights.pth",
            "scaler": None,
        },
        "Dog": {
            "type": "cnn",
            "path": "D:/chen Promoter work/web_server/S2_models_July_Dog/model_weights.pth",
            "scaler": None,
        },
        "Chicken": {
            "type": "cnn",
            "path": "D:/chen Promoter work/web_server/S2_models_July_Chicken/model_weights.pth",
            "scaler": None,
        },
        "Macaque": {
            "type": "cnn",
            "path": "D:/chen Promoter work/web_server/S2_models_July_macaque/model_weights.pth",
            "scaler": None,
        },
    }

    # Confidence threshold for species assignment. Below this, a promoter
    # is reported as "Unknown" species instead of forced into the closest match.
    SPECIES_CONFIDENCE_THRESHOLD = 0.55

    # ---------------------------------------------------------------
    # Model / sequence parameters
    # ---------------------------------------------------------------
    MAX_SEQ_LEN = 300
    EMBEDDING_DIM = 128
    NUM_FILTERS = [64, 128, 256, 512]
    KERNEL_SIZES = [3, 5, 7, 9]
    LSTM_HIDDEN_SIZE = 256
    LSTM_NUM_LAYERS = 2
    ATTENTION_DIM = 128
    DROPOUT_RATE = 0.3
    VOCAB_SIZE = 5
    NUCLEOTIDES = "ACGT"
    NT_TO_IDX = {nt: i + 1 for i, nt in enumerate("ACGT")}

    STAGE2_CNN_INPUT_CHANNELS = 4
    STAGE2_CNN_NUM_CLASSES = 1

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ---------------------------------------------------------------
    # Flask app paths
    # ---------------------------------------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
    ALLOWED_EXTENSIONS = {"txt", "fasta", "fa", "fna"}
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB upload limit


config = Config()
