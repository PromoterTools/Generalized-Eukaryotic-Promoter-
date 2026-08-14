# A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction?style=social)](https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction)
[![GitHub Forks](https://img.shields.io/github/forks/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction?style=social)](https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction/fork)
[![GitHub release](https://img.shields.io/github/v/release/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction?include_prereleases)](https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction/releases)

<p align="center">
  <img src="Fig. 1.png" alt="Graphical abstract of the two-stage eukaryotic promoter prediction framework" width="95%">
</p>

<p align="center"><b>Graphical abstract.</b> Sixteen EPDnew species were collected; 15 were used for Stage 1 model development and <i>Drosophila melanogaster</i> was withheld for cross-species evaluation. Stage 2 uses species-specific, CAGE-derived promoter-activity labels for six vertebrate species.</p>

> **Authors:** Muhammad Shujaat, Shi-Qing Mao  
> **Affiliation:** Institute for Advanced Study, Shenzhen University, Shenzhen, China  


---

## Overview

This repository contains the code, processed benchmark data, trained models, supplementary analyses, and deployment files for a two-stage framework for eukaryotic promoter analysis.

- **Stage 1 — promoter/non-promoter prediction:** a CNN–BiLSTM model with self-attention is trained on experimentally validated EPDnew promoters from **15 eukaryotic species** and GC-matched non-promoter sequences. All sequences used in the manuscript are **300 bp** long, spanning **−249 to +50 bp relative to the TSS**. *D. melanogaster* is withheld from model development and used as a separate cross-species binary evaluation set.
- **Stage 2 — CAGE-derived promoter-activity classification:** promoter-positive sequences are classified as **strong** or **weak** using species-specific models for human, mouse, rat, dog, chicken, and rhesus macaque. Labels are derived from FANTOM5 CAGE transcriptional activity, using the upper and lower quartiles of the species-specific TPM distribution.
- **Interpretability:** attention-based motif ranking is reported for the primary Stage 1 model. Nucleotide-level SHAP analysis is performed with a **separately trained one-hot surrogate CNN**; therefore, SHAP values explain the surrogate model directly and are interpreted only as approximate sequence-level evidence related to the primary model.

The Stage 2 models are **not species-identification models**. For Stage 2 inference, the user must provide the relevant species; confidence values from independently trained strong/weak classifiers are not compared to infer species identity.

---

## Key Results

### Stage 1

| Evaluation | Metric | Value |
|---|---|---:|
| Held-out Stage 1 test set | Accuracy | 0.9489 |
| Held-out Stage 1 test set | F1-score | 0.9580 |
| Held-out Stage 1 test set | ROC-AUC | 0.9742 |
| Held-out Stage 1 test set | PR-AUC | 0.9846 |
| 5-fold cross-validation | Accuracy | 0.9436 ± 0.0017 |
| 5-fold cross-validation | F1-score | 0.9536 ± 0.0013 |
| 5-fold cross-validation | ROC-AUC | 0.9727 ± 0.0020 |
| Withheld *D. melanogaster* binary evaluation | Accuracy | 0.948 |

The withheld *D. melanogaster* evaluation contains **16,972 promoters and 16,972 GC-matched non-promoters** and is kept outside Stage 1 model development.

### Stage 2

| Species | Best model | ROC-AUC |
|---|---|---:|
| Human | CNN | 0.912 |
| Mouse | XGBoost | 0.890 |
| Rat | CNN | 0.904 |
| Dog | CNN | 0.893 |
| Chicken | CNN | 0.871 |
| Rhesus macaque | CNN | 0.868 |

### Pooled Stage 2 baseline

A single all-species pooled CNN–BiLSTM baseline was evaluated for comparison. On the pooled held-out test set it achieved:

| Metric | Value |
|---|---:|
| Accuracy | 0.6186 |
| ROC-AUC | 0.6708 |
| PR-AUC | 0.6948 |
| Precision | 0.7767 |
| Recall | 0.3326 |
| F1-score | 0.4658 |
| MCC | 0.2890 |
| Balanced accuracy | 0.6185 |

Per-species ROC-AUC values from the pooled model were **0.828 (human), 0.632 (mouse), 0.685 (rat), 0.690 (dog), 0.483 (chicken), and 0.506 (macaque)**, with a macro-average species AUC of **0.637**. Because the pooled baseline and species-specific models do not use identical architectures, these results show that simple pooling did not improve performance in the present datasets but do not establish universal superiority of species-specific modelling.

---

## Validation and Reviewer-Requested Analyses

The revision includes the following additional analyses:

- **Stage 1 five-fold cross-validation:** per-fold accuracy, F1-score, and ROC-AUC are reported in the Supplementary Information.
- **Combined cross-validation confusion matrix:** precision 0.930, recall 0.978, specificity 0.893, and MCC approximately 0.884.
- **SHAP stability:** five independently trained surrogate CNNs were evaluated across folds; pairwise Spearman correlations of mean SHAP scores ranged from **0.91 to 0.96**.
- **Gene-aware validation:** gene-level partitioning was additionally examined where gene annotations were available; the human Stage 1 analysis achieved **94.12% accuracy and ROC-AUC 0.971**.
- **Stage 2 sample-size analysis:** CNN AUC showed a positive but non-significant monotonic association with dataset size (Spearman **r = 0.77, p = 0.072**), whereas XGBoost showed no clear monotonic association (**r = −0.09, p = 0.872**).
- **Matched downsampling:** at **n = 704**, XGBoost achieved higher AUC than CNN for human (**0.815 vs 0.775**) and rat (**0.802 vs 0.755**).
- **Sequence-diversity analysis:** normalized pairwise Hamming-distance distributions were compared between strong- and weak-activity promoters across the six Stage 2 species.
- **GC-controlled motif analysis:** k-mer analysis was repeated after GC normalization, and Fisher's exact tests with Benjamini–Hochberg false-discovery-rate correction were used for the reported statistical evaluation.
- **Pooled-versus-species-specific comparison:** the pooled Stage 2 baseline results are reported above and in the Supplementary Information.

These analyses are included to quantify stability, investigate possible sequence-composition effects, and clarify the scope of the species-wise Stage 2 results.

---

## Important Interpretation Notes

### CAGE-derived activity is context dependent

Stage 2 labels represent **CAGE-derived promoter activity**, not a context-independent intrinsic promoter property. For each species, promoter windows are matched to FANTOM5 CAGE peaks. When multiple CAGE peaks overlap one promoter window, their TPM values are averaged to obtain the representative activity used in the present dataset. Strong and weak labels are then defined relative to the species-specific activity distribution.

### Intermediate activity

The middle 50% of the species-specific activity distribution (Q25–Q75) is excluded from Stage 2 training to reduce label ambiguity. In the web interface, predictions close to the strong/weak decision boundary are flagged as **“Low Confidence — intermediate activity possible.”** This flag is a cautionary output and is not a separately trained biological third class.

### SHAP scope

SHAP analysis is conducted on a **surrogate one-hot CNN**, not directly on the primary integer-encoded CNN–BiLSTM. SHAP plots should therefore be interpreted as explanations of the surrogate classifier and as approximate evidence of related sequence-level patterns.

### Data-partition limitation

CD-HIT redundancy filtering at a 0.90 similarity threshold is applied before Stage 1 data partitioning. The full multi-species split is sequence based, so residual relatedness among alternative TSSs from the same locus cannot be completely excluded. Gene-aware validation was additionally performed where suitable gene annotations were available.

---

## Repository Structure

```text
Generalized-Eukaryotic-Promoter-Prediction/
│
├── README.md
├── LICENSE
├── environment.yml
├── requirements.txt
├── Dockerfile
│
├── data/
│   ├── stage1/
│   │   ├── train.fasta
│   │   ├── val.fasta
│   │   ├── test.fasta
│   │   └── drosophila_test.fasta
│   └── stage2/
│       ├── human/
│       ├── mouse/
│       ├── rat/
│       ├── dog/
│       ├── chicken/
│       └── macaque/
│
├── models/
│   ├── stage1_cnn_bilstm.pt
│   ├── stage2_human_cnn.pt
│   ├── stage2_mouse_xgboost.pkl
│   ├── stage2_rat_cnn.pt
│   ├── stage2_dog_cnn.pt
│   ├── stage2_chicken_cnn.pt
│   └── stage2_macaque_cnn.pt
│
├── src/
│   ├── predict_stage1.py
│   ├── predict_stage2.py
│   ├── predict_pipeline.py
│   ├── train_stage1.py
│   ├── train_stage2.py
│   ├── model_stage1.py
│   ├── model_stage2.py
│   └── encoding.py
│
├── web_server/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── figures/
│   ├── graphical_abstract.jpg
│   └── generate_figures.py
│
├── supplementary/
│   ├── SupplementaryFile.docx
│   └── table_s2_cage_files.csv
│
└── results/
    └── example_predictions.csv
```

> **Repository consistency check:** before public release, verify that every file/path shown above exists in the repository. Remove entries that are not distributed.

---

## Installation

### Option 1 — Conda (recommended)

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction.git
cd Generalized-Eukaryotic-Promoter-Prediction
conda env create -f environment.yml
conda activate promoternet
python src/predict_stage1.py --help
```

A successful `--help` call verifies that the environment can load the prediction entry point.

### Option 2 — Docker

Build the container:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction.git
cd Generalized-Eukaryotic-Promoter-Prediction
docker build -t promoternet .
```

Run Stage 1:

```bash
docker run --rm \
  -v "$(pwd)/data:/data" \
  -v "$(pwd)/results:/results" \
  promoternet \
  python src/predict_stage1.py \
  --input /data/example.fasta \
  --output /results/stage1_predictions.csv
```

Run the local web application:

```bash
docker run --rm -p 5000:5000 promoternet python web_server/app.py
```

Then open `http://localhost:5000`.

### Option 3 — pip

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-Prediction.git
cd Generalized-Eukaryotic-Promoter-Prediction
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
python src/predict_stage1.py --help
```

For CUDA acceleration, install the PyTorch build appropriate for the local CUDA environment before running GPU inference.

---

## Quick Usage Tutorial

### Stage 1 — promoter prediction

```bash
python src/predict_stage1.py \
  --input your_sequences.fasta \
  --model models/stage1_cnn_bilstm.pt \
  --output results/stage1_predictions.csv \
  --threshold 0.5
```

Expected Stage 1 output fields:

| Column | Description |
|---|---|
| `sequence_id` | FASTA sequence identifier |
| `stage1_probability` | predicted promoter probability |
| `stage1_prediction` | `Promoter` or `Non-Promoter` |

### Stage 2 — promoter activity classification

Stage 2 should be applied only to promoter-positive or experimentally verified promoter sequences. **Species selection is required.**

```bash
python src/predict_stage2.py \
  --input promoter_sequences.fasta \
  --species human \
  --output results/stage2_predictions.csv
```

Supported `--species` values:

| Value | Organism | Final model | Reported assembly |
|---|---|---|---|
| `human` | *Homo sapiens* | CNN | hg38 |
| `mouse` | *Mus musculus* | XGBoost | mm9 |
| `rat` | *Rattus norvegicus* | CNN | rn6 |
| `dog` | *Canis lupus familiaris* | CNN | canFam3 |
| `chicken` | *Gallus gallus* | CNN | galGal5 |
| `macaque` | *Macaca mulatta* | CNN | rheMac8 |

Expected Stage 2 output fields:

| Column | Description |
|---|---|
| `species` | user-selected species |
| `stage2_probability` | predicted strong-activity probability |
| `stage2_prediction` | `Strong`, `Weak`, or `Low Confidence` |

### Full two-stage pipeline

```bash
python src/predict_pipeline.py \
  --input your_sequences.fasta \
  --species human \
  --output results/full_predictions.csv \
  --stage1_threshold 0.5
```

Sequences classified as non-promoters in Stage 1 are excluded from Stage 2. The pipeline does **not** use cross-model confidence scores for species identification.

---

## Web Server

A hosted implementation is available at:

**https://promoter-prediction-app.onrender.com/**

To run locally:

```bash
python web_server/app.py
```

Then open `http://localhost:5000`.

The interface supports:

- pasted single-sequence or multi-FASTA input;
- `.fasta` and `.txt` upload;
- adjustable Stage 1 probability threshold (default 0.5);
- **required species selection for Stage 2**;
- Stage 1 promoter probability and class;
- Stage 2 strong/weak CAGE-derived activity prediction;
- low-confidence warning for borderline Stage 2 predictions;
- downloadable prediction output.

> The Stage 2 species-specific classifiers were trained for strong/weak activity classification, not species recognition. Do not infer species by comparing confidence scores across independently trained Stage 2 models.

---

## Input Format

For manuscript reproduction, sequences should be **exactly 300 bp**, corresponding to positions **−249 to +50 bp relative to the TSS**.

```fasta
>sequence_id_1
ACGT...300_bp_sequence...
>sequence_id_2
TGCA...300_bp_sequence...
```

- Standard DNA bases A, C, G, and T are supported.
- Ambiguous bases should be handled consistently with the preprocessing script used to reproduce the manuscript analysis.
- If a convenience inference script supports padding or trimming, that behavior should not be treated as equivalent to the manuscript's fixed 300 bp benchmark construction.

---

## Feature Encoding Schemes

Eight sequence-encoding schemes were evaluated:

1. One-Hot Encoding
2. Integer Encoding
3. Nucleotide Chemical Properties (NCP)
4. Physical Properties Encoding
5. Dinucleotide Composition
6. k-mer Frequency Encoding
7. Pseudo Nucleotide Composition (PseKNC)
8. DNA Duplex Stability (DDS) Encoding

The complete mathematical definitions, equations, and parameter descriptions are provided in **Supplementary File 1, Supplementary Note S1**.

---

## Datasets

### Stage 1

- Source: EPDnew experimentally supported promoters.
- Promoter sequences collected from 16 species.
- **15 species used for development**; *D. melanogaster* withheld entirely for cross-species evaluation.
- Negative samples: species-matched GC-balanced non-promoter sequences.
- Sequence length: 300 bp (−249 to +50 relative to TSS).
- Redundancy filtering: CD-HIT at 0.90 sequence-similarity threshold before partitioning.
- Development split: 70% training / 15% validation / 15% held-out test, stratified to approximately preserve species and class proportions.

**Stage 1 development species (15):**

*Arabidopsis thaliana*, *Apis mellifera*, *Canis lupus familiaris*, *Homo sapiens*, *Gallus gallus*, *Macaca mulatta*, *Plasmodium falciparum*, *Rattus norvegicus*, *Saccharomyces cerevisiae*, *Hordeum vulgare*, *Schizosaccharomyces pombe*, *Caenorhabditis elegans*, *Danio rerio*, *Zea mays*, and *Mus musculus*.

**Withheld cross-species test:**

*Drosophila melanogaster* — 16,972 promoters + 16,972 GC-matched non-promoters.

### Stage 2

- Species: human, mouse, rat, dog, chicken, and rhesus macaque.
- Source of activity labels: FANTOM5 CAGE peak expression data.
- Promoter window: the same 300 bp TSS-centered window used in the study.
- Multiple overlapping CAGE peaks within one promoter window: mean TPM aggregation.
- Strong activity: TPM ≥ species-specific Q75.
- Weak activity: TPM ≤ species-specific Q25.
- Intermediate activity (Q25–Q75): excluded from model training/evaluation.

Full Stage 2 counts and CAGE-file information are provided in the Supplementary Information.

---

## Trained Models

| File | Description | Format |
|---|---|---|
| `stage1_cnn_bilstm.pt` | Stage 1 CNN–BiLSTM self-attention model | PyTorch |
| `stage2_human_cnn.pt` | Human Stage 2 CNN | PyTorch |
| `stage2_mouse_xgboost.pkl` | Mouse Stage 2 XGBoost | pickle |
| `stage2_rat_cnn.pt` | Rat Stage 2 CNN | PyTorch |
| `stage2_dog_cnn.pt` | Dog Stage 2 CNN | PyTorch |
| `stage2_chicken_cnn.pt` | Chicken Stage 2 CNN | PyTorch |
| `stage2_macaque_cnn.pt` | Macaque Stage 2 CNN | PyTorch |

Complete hyperparameters, random seeds, and supplementary validation results should be distributed with the release so that the reported experiments can be reproduced.

---

## Reproducing the Reported Analyses

For reproducibility, the public release should contain the exact processed data/split identifiers, model weights, and scripts used for the manuscript analyses. At minimum, users should be able to reproduce:

1. Stage 1 held-out test metrics.
2. Stage 1 five-fold cross-validation results.
3. Withheld *D. melanogaster* binary evaluation.
4. Six species-specific Stage 2 evaluations.
5. Pooled Stage 2 baseline.
6. Stage 2 sample-size/downsampling analysis.
7. Hamming-distance sequence-diversity analysis.
8. Surrogate-CNN SHAP stability analysis.
9. GC-controlled motif analysis and FDR-corrected statistical testing.
10. Main and supplementary figures.

Where randomness is used, publish the corresponding seed and split file together with the result.

---

## Installation and Usage Video

The editor requested a complete demonstration recorded on a clean computer/server showing repository download, installation, execution, and result display.

**Permanent video tutorial URL:** `ADD_PERMANENT_VIDEO_URL_BEFORE_SUBMISSION`

The video should demonstrate, in order:

1. cloning/downloading the repository;
2. creating the Conda environment or building the Docker image;
3. running the installation verification command;
4. executing Stage 1 on the included test/example data;
5. executing Stage 2 with an explicitly selected species;
6. launching the web server;
7. displaying and downloading prediction results.

> Replace the placeholder above with the permanent public video URL before journal resubmission.

---

## Troubleshooting

**CUDA out-of-memory**  
Reduce the inference batch size or run on CPU.

**Input sequence is not 300 bp**  
For reproduction of manuscript results, construct the same −249 to +50 bp promoter window rather than relying on automatic padding/trimming.

**Stage 2 returns Low Confidence**  
The Stage 2 models are trained on the upper and lower quartiles of the CAGE activity distribution. A probability near the decision boundary may correspond to an intermediate-activity sequence and should be interpreted cautiously.

**Species is not supported in Stage 2**  
Use Stage 1 only. Stage 2 is currently limited to the six species for which the CAGE-derived activity datasets were constructed.

**Web server does not start locally**  
Check that the configured port is free and that all model files are present at the paths expected by `web_server/app.py`.

---

## Citation

If you use this repository, please cite the manuscript after publication. Until a final bibliographic record is available, use:

```bibtex
@misc{shujaat2026eukaryoticpromoter,
  title  = {A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification},
  author = {Shujaat, Muhammad and Mao, Shi-Qing},
  year   = {2026},
  note   = {Manuscript under revision}
}
```

Do not replace this with a journal volume, issue, or DOI until those details are officially assigned.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- EPDnew for experimentally supported eukaryotic promoter data.
- FANTOM5 for CAGE-based transcriptional activity resources.
- Shenzhen University, Institute for Advanced Study.

---

## Contact

For software issues, please open a GitHub Issue. contact **Dr. Shujaat (shujaat@szu.edu.cn)**.
