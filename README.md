# 🧬 Species-aware Eukaryotic Promoter Prediction  
### A Two-stage Framework for Generalized Promoter Recognition and Strong/Weak Promoter Classification
<img width="1672" height="941" alt="Graphical Abstract" src="https://github.com/user-attachments/assets/638dcb59-386c-456c-82df-17e56eedb794" />
# PromoterNet: A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction?style=social)](https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction)

> **Authors:** Muhammad Shujaat, Shi-Qing Mao
> **Affiliation:** Institute for Advanced Study, Shenzhen University, Shenzhen, China
> **Contact:** msq@szu.edu.cn

---

## Table of Contents

- [Overview](#overview)
- [Key Results](#key-results)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
  - [Option 1: Conda (Recommended)](#option-1-conda-recommended)
  - [Option 2: Docker](#option-2-docker)
  - [Option 3: pip](#option-3-pip)
- [Usage Tutorial](#usage-tutorial)
  - [Stage 1: Promoter Prediction](#stage-1-promoter-prediction)
  - [Stage 2: Promoter Strength Classification](#stage-2-promoter-strength-classification)
  - [Running Both Stages Together](#running-both-stages-together)
  - [Web Server](#web-server)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Datasets](#datasets)
- [Trained Models](#trained-models)
- [Species Coverage](#species-coverage)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)

---

## Overview

This repository provides the full implementation of a **two-stage computational framework** for eukaryotic promoter analysis:

- **Stage 1 — Promoter Identification:** A CNN–BiLSTM model with a self-attention mechanism trained on experimentally validated EPDnew promoters from 15 eukaryotic species. Sequences are 300 bp in length spanning from −249 bp upstream to +50 bp downstream of the TSS.

- **Stage 2 — Promoter Strength Classification:** Species-specific CNN or XGBoost classifiers that classify promoters as **strong** or **weak** based on FANTOM5 CAGE-derived transcriptional activity (TPM). Separate models are trained per species to account for species-dependent motif-switching patterns.

The key biological motivation for species-wise modeling is that the same k-mer motif may be enriched among **strong** promoters in human but among **weak** promoters in chicken or macaque. Training a single pooled model across species sends conflicting training signals; species-wise models avoid this entirely.

---

## Key Results

| Task | Metric | Value |
|---|---|---|
| Stage 1 — Promoter Identification | Accuracy | 94.89% |
| Stage 1 | F1-score | 0.958 |
| Stage 1 | ROC-AUC | 0.9742 |
| Stage 1 | PR-AUC | 0.9846 |
| Stage 1 — Cross-species (*D. melanogaster*, withheld) | Accuracy | 94.8% |
| Stage 2 — Human | CNN AUC | 0.912 |
| Stage 2 — Rat | CNN AUC | 0.904 |
| Stage 2 — Dog | CNN AUC | 0.893 |
| Stage 2 — Chicken | CNN AUC | 0.871 |
| Stage 2 — Macaque | CNN AUC | 0.868 |
| Stage 2 — Mouse | XGBoost AUC | 0.890 |

5-fold cross-validation: **94.71% ± 0.41% accuracy**, F1 0.956 ± 0.005, ROC-AUC 0.973 ± 0.003.

---

## Repository Structure

```
Generalized-Eukaryotic-Promoter-Prediction/
│
├── README.md                        # This file
├── environment.yml                  # Conda environment specification
├── Dockerfile                       # Docker container definition
├── requirements.txt                 # pip dependencies
│
├── data/
│   ├── stage1/
│   │   ├── train.fasta              # Stage 1 training sequences (15 species)
│   │   ├── val.fasta                # Validation set
│   │   ├── test.fasta               # Independent test set
│   │   └── drosophila_test.fasta    # Withheld Drosophila evaluation set
│   └── stage2/
│       ├── human/
│       │   ├── strong.fasta
│       │   └── weak.fasta
│       ├── mouse/
│       ├── rat/
│       ├── dog/
│       ├── chicken/
│       └── macaque/
│
├── models/
│   ├── stage1_cnn_bilstm.pt         # Stage 1 trained model weights (PyTorch)
│   ├── stage2_human_cnn.pt
│   ├── stage2_mouse_xgboost.pkl
│   ├── stage2_rat_cnn.pt
│   ├── stage2_dog_cnn.pt
│   ├── stage2_chicken_cnn.pt
│   └── stage2_macaque_cnn.pt
│
├── src/
│   ├── predict_stage1.py            # Stage 1 inference script
│   ├── predict_stage2.py            # Stage 2 inference script
│   ├── predict_pipeline.py          # Full two-stage pipeline
│   ├── train_stage1.py              # Stage 1 training script
│   ├── train_stage2.py              # Stage 2 training script
│   ├── model_stage1.py              # CNN-BiLSTM architecture definition
│   ├── model_stage2.py              # Stage 2 CNN architecture definition
│   └── encoding.py                  # Sequence encoding utilities
│
├── web_server/
│   ├── app.py                       # Flask web server
│   ├── templates/
│   └── static/
│
├── figures/
│   └── generate_figures.py          # Reproduces all manuscript figures
│
└── supplementary/
    ├── SupplementaryFile.docx
    └── table_s2_cage_files.csv
```

---

## Installation

### Option 1: Conda (Recommended)

This is the recommended installation method. It handles all dependencies including PyTorch, XGBoost, and BioPython automatically.

**Step 1: Clone the repository**

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction.git
cd Generalized-Eukaryotic-Promoter-Prediction
```

**Step 2: Create the conda environment**

```bash
conda env create -f environment.yml
```

**Step 3: Activate the environment**

```bash
conda activate promoternet
```

**Step 4: Verify installation**

```bash
python src/predict_stage1.py --help
```

You should see the usage message if installation was successful.

---

### Option 2: Docker

Docker is the easiest way to ensure a fully reproducible environment with no dependency conflicts.

**Step 1: Pull or build the image**

```bash
# Build from Dockerfile
docker build -t promoternet .

# OR pull from Docker Hub (if available)
docker pull shujaatmuhammad/promoternet:latest
```

**Step 2: Run a prediction inside the container**

```bash
docker run --rm \
  -v $(pwd)/your_sequences.fasta:/data/input.fasta \
  -v $(pwd)/results:/data/output \
  promoternet \
  python src/predict_pipeline.py \
    --input /data/input.fasta \
    --output /data/output/predictions.csv
```

**Step 3: Run the web server inside Docker**

```bash
docker run -p 5000:5000 promoternet python web_server/app.py
```

Then open your browser at `http://localhost:5000`.

---

### Option 3: pip

If you prefer pip without conda:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction.git
cd Generalized-Eukaryotic-Promoter-Prediction
pip install -r requirements.txt
```

> **Note:** For GPU acceleration (recommended for large datasets), install the appropriate PyTorch version for your CUDA version from https://pytorch.org/get-started/locally/ before running pip install.

---

## Usage Tutorial

### Stage 1: Promoter Prediction

Run Stage 1 (promoter vs. non-promoter) on a FASTA file:

```bash
python src/predict_stage1.py \
  --input your_sequences.fasta \
  --model models/stage1_cnn_bilstm.pt \
  --output results/stage1_predictions.csv \
  --threshold 0.5
```

**Arguments:**

| Argument | Description | Default |
|---|---|---|
| `--input` | Path to input FASTA file | required |
| `--model` | Path to trained Stage 1 model weights | `models/stage1_cnn_bilstm.pt` |
| `--output` | Path to output CSV file | `predictions.csv` |
| `--threshold` | Promoter probability decision threshold | `0.5` |
| `--batch_size` | Batch size for inference | `32` |
| `--device` | `cpu` or `cuda` | auto-detected |

**Example with a single sequence:**

```bash
echo ">test_seq
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" > test.fasta

python src/predict_stage1.py --input test.fasta --output test_result.csv
cat test_result.csv
```

---

### Stage 2: Promoter Strength Classification

Run Stage 2 (strong vs. weak) on sequences already confirmed as promoters. You must specify the species:

```bash
python src/predict_stage2.py \
  --input promoter_sequences.fasta \
  --species human \
  --output results/stage2_predictions.csv
```

**Supported species values:**

| `--species` value | Organism | Model type | Genome assembly |
|---|---|---|---|
| `human` | *Homo sapiens* | CNN | hg38 |
| `mouse` | *Mus musculus* | XGBoost | mm9 |
| `rat` | *Rattus norvegicus* | CNN | rn6 |
| `dog` | *Canis lupus familiaris* | CNN | canFam3 |
| `chicken` | *Gallus gallus* | CNN | galGal5 |
| `macaque` | *Macaca mulatta* | CNN | rheMac8 |

**Arguments:**

| Argument | Description | Default |
|---|---|---|
| `--input` | Path to input FASTA file (promoters only) | required |
| `--species` | Target species (see table above) | required |
| `--output` | Path to output CSV file | `stage2_predictions.csv` |
| `--threshold` | Strong/weak decision threshold | `0.5` |

---

### Running Both Stages Together

The full pipeline script runs Stage 1 and Stage 2 sequentially on any FASTA file:

```bash
python src/predict_pipeline.py \
  --input your_sequences.fasta \
  --species human \
  --output results/full_predictions.csv \
  --stage1_threshold 0.5
```

Sequences that Stage 1 classifies as **non-promoters** are excluded from Stage 2 automatically.

**Automated species assignment (no species specified):**

If you omit `--species`, the pipeline evaluates each promoter-positive sequence against all six species models and returns the highest-confidence assignment. Note that confidence scores from independently trained binary classifiers are heuristic — specify `--species` whenever you know the organism of origin for more reliable Stage 2 results.

```bash
python src/predict_pipeline.py \
  --input your_sequences.fasta \
  --output results/full_predictions.csv
  # no --species: auto-assigns, labeled "Auto-assigned (heuristic)"
```

---

### Web Server

To launch the web server locally:

```bash
python web_server/app.py
```

Then open your browser at `http://localhost:5000`.

The web server accepts:
- Pasted sequences (single or multi-FASTA format)
- Uploaded `.fasta` or `.txt` files
- Adjustable Stage 1 decision threshold (default 0.5)
- Optional species selection dropdown (recommended) or automated species assignment

Output includes:
- Stage 1 promoter probability and class per sequence
- Stage 2 predicted strength (strong/weak) and confidence score
- Species-resolved summary panel with interactive graphics
- Downloadable FASTA file of predicted promoter sequences

> **Note:** Sequences with predicted strong/weak probability between 0.4 and 0.6 are flagged as **"Low Confidence — intermediate activity possible"** and should be interpreted with caution.

---

## Input Format

All input files must be in **FASTA format**. Each sequence must be exactly **300 bp** in length, spanning from −249 bp upstream to +50 bp downstream of the TSS.

```fasta
>sequence_id_1
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG...  (300 bp)
>sequence_id_2
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG...  (300 bp)
```

**Important:**
- Sequences shorter or longer than 300 bp will be padded or trimmed automatically, but this may reduce prediction accuracy.
- Only standard DNA bases (A, C, G, T) are supported. Ambiguous bases (N) are allowed but may affect performance.
- For Stage 2, only submit sequences already predicted as promoters by Stage 1 (or experimentally verified promoters).

---

## Output Format

The output CSV file contains the following columns:

**Stage 1 output:**

| Column | Description |
|---|---|
| `sequence_id` | Sequence identifier from FASTA header |
| `stage1_probability` | Promoter probability (0–1) |
| `stage1_prediction` | `Promoter` or `Non-Promoter` |

**Stage 2 output (appended to Stage 1 rows where applicable):**

| Column | Description |
|---|---|
| `species` | Species assigned (user-specified or auto-assigned) |
| `species_assignment` | `User-specified` or `Auto-assigned (heuristic)` |
| `stage2_probability` | Strong promoter probability (0–1) |
| `stage2_prediction` | `Strong`, `Weak`, or `Low Confidence` |

---

## Datasets

All processed datasets used in the manuscript are available in the `data/` directory:

**Stage 1:**
- Positive sequences: 15 eukaryotic species from EPDnew (experimentally validated TSS-mapped promoters)
- Negative sequences: GC-content-matched non-promoter sequences from non-coding genomic regions
- Redundancy removed using CD-HIT (similarity threshold 0.90)
- Split: 70% train / 15% validation / 15% test (stratified by species)
- *D. melanogaster* (16,972 promoters + 16,972 matched non-promoters) withheld entirely for cross-species evaluation

**Stage 2:**
- Labels derived from FANTOM5 CAGE peak data (mean TPM across overlapping peaks per promoter window)
- Upper quartile (TPM ≥ Q75) → Strong promoters
- Lower quartile (TPM ≤ Q25) → Weak promoters
- Intermediate promoters (Q25–Q75) excluded to reduce label ambiguity
- Genome assemblies: hg38 (human), mm9 (mouse), rn6 (rat), canFam3 (dog), galGal5 (chicken), rheMac8 (macaque)

Full dataset statistics are provided in Supplementary Table S2.

---

## Trained Models

Pre-trained model weights are included in the `models/` directory:

| File | Description | Format |
|---|---|---|
| `stage1_cnn_bilstm.pt` | Stage 1 CNN–BiLSTM attention model | PyTorch |
| `stage2_human_cnn.pt` | Stage 2 Human CNN | PyTorch |
| `stage2_rat_cnn.pt` | Stage 2 Rat CNN | PyTorch |
| `stage2_dog_cnn.pt` | Stage 2 Dog CNN | PyTorch |
| `stage2_chicken_cnn.pt` | Stage 2 Chicken CNN | PyTorch |
| `stage2_macaque_cnn.pt` | Stage 2 Macaque CNN | PyTorch |
| `stage2_mouse_xgboost.pkl` | Stage 2 Mouse XGBoost | scikit-learn pickle |

All hyperparameters are documented in Supplementary Table S4.

---

## Species Coverage

**Stage 1 training species (15):**

| Group | Species |
|---|---|
| Vertebrates | *Homo sapiens*, *Mus musculus*, *Rattus norvegicus*, *Canis lupus familiaris*, *Gallus gallus*, *Macaca mulatta*, *Danio rerio*, *Xenopus tropicalis* |
| Invertebrates | *Caenorhabditis elegans* |
| Plants | *Arabidopsis thaliana*, *Zea mays*, *Oryza sativa* |
| Fungi | *Saccharomyces cerevisiae* |
| Protist | *Dictyostelium discoideum* |

**Stage 1 withheld (cross-species evaluation):**
- *Drosophila melanogaster* — 16,972 promoters + 16,972 GC-matched non-promoters

**Stage 2 species (6):**
- Human, Mouse, Rat, Dog, Chicken, Macaque

---

## Troubleshooting

**Q: I get a CUDA out-of-memory error.**
Reduce the batch size: `--batch_size 8` or run on CPU with `--device cpu`.

**Q: My sequences are not exactly 300 bp.**
The pipeline pads shorter sequences with N and trims longer sequences to 300 bp from the center. For best results, prepare 300 bp windows centered on your TSS coordinates before running predictions.

**Q: Stage 2 shows "Low Confidence" for many sequences.**
This is expected for sequences with intermediate transcriptional activity. The models are trained on the upper and lower quartiles of the CAGE expression distribution; borderline sequences near the median will receive confidence scores close to 0.5.

**Q: The web server is not loading.**
Ensure port 5000 is not in use. Try: `python web_server/app.py --port 8080` and open `http://localhost:8080`.

**Q: I want to predict for a species not in the Stage 2 list.**
Use Stage 1 only for promoter/non-promoter classification. Stage 2 is currently limited to six species with available FANTOM5 CAGE data.

**Q: conda env create fails.**
Try updating conda first: `conda update -n base conda`, then retry. Alternatively, use the Docker option.

---

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{shujaat2024promoternet,
  title   = {A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction
             and Promoter Strength Classification},
  author  = {Shujaat, Muhammad and Mao, Shi-Qing},
  journal = {iMetaOmics},
  year    = {2024},
  note    = {Under revision}
}
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- EPDnew database for experimentally validated promoter sequences
- FANTOM5 consortium for CAGE peak expression data
- Shenzhen University Institute for Advanced Study

---

*For questions, issues, or collaboration inquiries, please open a GitHub Issue or contact msq@szu.edu.cn.*
