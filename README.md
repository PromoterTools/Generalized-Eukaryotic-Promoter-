

## A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification

**PromoterNet** is a two-stage computational framework for:

1. **Generalized promoter recognition** across eukaryotic species, and
2. **Species-specific CAGE-derived promoter activity classification** for promoter-positive sequences.

The framework combines a CNN-BiLSTM model with self-attention for Stage 1 and species-specific CNN/XGBoost models for Stage 2. It also provides attention-based sequence interpretation, surrogate-CNN SHAP analysis, and an interactive Flask web server.

![Graphical abstract]  <img src="Fig. 1.png" alt="Graphical abstract of the two-stage eukaryotic promoter prediction framework" width="95%">

---

## Web server

**Public web server:**  
https://promoter-prediction-app.onrender.com/

> **Note:** The public deployment may require a short cold-start period after inactivity before the interface becomes available.

---

## Overview

PromoterNet separates two related but distinct prediction tasks.

### Stage 1 — Promoter vs non-promoter

A 300-bp DNA window spanning **−249 to +50 bp relative to a putative transcription start site (TSS)** is classified as promoter or non-promoter using a multi-species CNN-BiLSTM model with self-attention.

### Stage 2 — Species-specific promoter activity

Sequences predicted as promoters are evaluated using the **known target species** selected by the user. Stage 2 predicts whether the promoter belongs to the upper- or lower-activity group defined from FANTOM5 CAGE measurements within that species.

The current Stage 2 labels are:

- **Strong / high activity:** upper quartile (Q75 and above)
- **Weak / low activity:** lower quartile (Q25 and below)

The middle 50% of promoters was excluded from binary Stage 2 training.

> PromoterNet does **not** use confidence values from independently trained Stage 2 models to infer species identity. The target species is supplied by the user.

---

## Important scope

PromoterNet is a **candidate-window classifier**, not a genome-wide promoter scanner.

Input sequences for the released models should be **300 bp long**, corresponding to the same −249/+50 TSS-centered window used for model development. Arbitrary-length genomic regions must first be converted into appropriate candidate windows before prediction.

The Stage 2 labels represent **relative CAGE-derived promoter activity within each species**. They should not be interpreted as universal, tissue-independent intrinsic promoter strength.

---

## Supported Stage 2 species

| Species | Stage 2 model |
|---|---|
| Human | CNN |
| Mouse | XGBoost |
| Rat | CNN |
| Dog | CNN |
| Chicken | CNN |
| Rhesus macaque | CNN |

---

## Key results

### Stage 1 — Independent held-out evaluation

| Metric | Value |
|---|---:|
| Accuracy | 0.9489 |
| F1-score | 0.958 |
| ROC-AUC | 0.9742 |
| PR-AUC | 0.9846 |

### Stage 1 — Five-fold cross-validation

| Metric | Mean ± SD |
|---|---:|
| Accuracy | 0.9436 ± 0.0017 |
| F1-score | 0.9536 ± 0.0013 |
| ROC-AUC | 0.9727 ± 0.0020 |

### Completely withheld *Drosophila melanogaster*

The independent cross-species evaluation contains:

- 16,972 promoter sequences
- 16,972 GC-matched non-promoter sequences
- 33,944 total sequences
- Overall binary accuracy: **94.8%**

### Stage 2 — Best species-specific ROC-AUC

| Species | Best model | ROC-AUC |
|---|---|---:|
| Human | CNN | 0.912 |
| Mouse | XGBoost | 0.890 |
| Rat | CNN | 0.904 |
| Dog | CNN | 0.893 |
| Chicken | CNN | 0.871 |
| Rhesus macaque | CNN | 0.868 |

### Pooled Stage 2 baseline

| Metric | Value |
|---|---:|
| Accuracy | 0.619 |
| ROC-AUC | 0.671 |
| PR-AUC | 0.695 |
| Precision | 0.777 |
| Recall | 0.333 |
| F1-score | 0.466 |
| MCC | 0.289 |
| Balanced accuracy | 0.619 |

The pooled analysis is reported as a baseline rather than a strict architecture-matched ablation.

---

## Repository contents

The repository provides the deployed web-server code, configuration files, dependency specification, processed test data, trained Stage 2 model files, and manuscript-related figures/resources.

Key files include:

```text
README.md
app.py
config.py
model_utils.py
requirements.txt
independent_test_split.csv

Human_model_weights.pth
Mouse_xgboost_model.pkl
Mouse_scaler.pkl
RAT_model_weights.pth
Dog_model_weights.pth
Chicken_model_weights.pth
macaque_model_weights.pth

templates/
static/
uploads/
outputs/
```


---

## Installation

### Option 1 — Python virtual environment

Clone the repository:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-.git
cd Generalized-Eukaryotic-Promoter-
```

Create and activate a virtual environment.

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Launch the web server:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### Option 2 — Conda

If `environment.yml` is distributed with the release:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-.git
cd Generalized-Eukaryotic-Promoter-
conda env create -f environment.yml
conda activate promoternet
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Option 3 — Docker

If `Dockerfile` is distributed with the release:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-.git
cd Generalized-Eukaryotic-Promoter-
docker build -t promoternet .
docker run --rm -p 5000:5000 promoternet python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Web-server tutorial

### 1. Prepare the input

PromoterNet accepts:

- a single 300-bp DNA sequence,
- a multi-FASTA block,
- a `.txt`, `.fasta`, `.fa`, or `.fna` file containing one or more sequences.

### 2. Set the Stage 1 threshold

The default promoter-probability threshold is:

```text
0.5
```

Sequences with Stage 1 probability at or above the selected threshold are classified as promoter candidates.

### 3. Select the known Stage 2 species

For promoter-activity classification, select the known target species:

- Human
- Mouse
- Rat
- Dog
- Chicken
- Rhesus macaque

Only the corresponding Stage 2 model is used for that sequence.

### 4. Run prediction

Click **Predict**.

The interface reports:

- Stage 1 promoter probability,
- promoter/non-promoter classification,
- Stage 2 activity classification for promoter-positive inputs,
- result summaries and visualizations.

### 5. Download outputs

Available outputs include:

- predicted promoter sequences in FASTA format,
- generated result charts,
- per-sequence prediction information.

Use **Reset** to clear the current analysis and begin a new prediction.

---

## Example input

FASTA format:

```text
>example_1
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
...
```

Each sequence supplied to the released model should contain **300 nucleotides**.

---

## Data and benchmark construction

### Stage 1

Promoter sequences were obtained from **EPDnew**. Species-matched non-promoter sequences were constructed with GC-content matching. Redundancy was reduced using CD-HIT before model development.

Fifteen species were used for Stage 1 development, while *D. melanogaster* was kept completely outside model development for independent cross-species evaluation.

### Stage 2

Species-specific promoter activity labels were derived using **FANTOM5 CAGE** data.

Within each species:

- the upper activity quartile was labeled strong/high activity,
- the lower activity quartile was labeled weak/low activity,
- the middle 50% was excluded from binary training.

The processed datasets, exact sample counts, genome-build information, CAGE aggregation details, validation analyses, and supplementary statistics are documented in the accompanying manuscript and Supporting Information.

---

## Model interpretation

Two complementary interpretation strategies are used.

### Attention analysis

Attention weights from the primary Stage 1 CNN-BiLSTM model are used to identify promoter-associated sequence regions and motifs.

### Surrogate-CNN SHAP analysis

SHAP analysis is performed using a **surrogate one-hot CNN**, not directly on the primary CNN-BiLSTM model.

Accordingly, SHAP-associated k-mers and nucleotide-level contributions are interpreted as **complementary model-associated evidence**, not as direct attribution of the primary CNN-BiLSTM.


---

## Reproducibility

The repository provides the inference code, dependency specification, processed test data, released trained models, and configuration used by the web server.

For the deployed inference workflow:

```bash
git clone https://github.com/ShujaatMuhammad/Generalized-Eukaryotic-Promoter-.git
cd Generalized-Eukaryotic-Promoter-
pip install -r requirements.txt
python app.py
```

The released independent test split is provided as:

```text
independent_test_split.csv
```

Model files used by the Stage 2 web-server implementation are distributed with the repository/release.

Experimental details including cross-validation, gene-aware validation, pooled modeling, downsampling, motif statistics, and GC-controlled analyses are reported in the Supporting Information associated with the manuscript.

---

## Limitations

PromoterNet should be interpreted within the scope of the released benchmark.

- The current models classify predefined **300-bp TSS-centered windows** rather than performing unrestricted genome-wide scanning.
- Stage 2 activity labels are based on upper/lower FANTOM5 CAGE quartiles within individual species.
- The excluded middle 50% is **not** a separately trained third class.
- CAGE activity is tissue- and condition-dependent.
- Stage 2 performance can be sensitive to the amount and composition of species-specific labeled data.
- SHAP interpretation is based on a surrogate CNN rather than direct SHAP attribution of the primary CNN-BiLSTM.
- The pooled Stage 2 experiment is a baseline and not a strict architecture-controlled ablation.

---

## Citation

If you use PromoterNet, please cite the associated manuscript:

> Muhammad Shujaat and Shi-Qing Mao. *A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification.*

A formal journal citation can be added after publication.

---

## Authors

**Muhammad Shujaat**  
Shenzhen University

**Shi-Qing Mao**  
Shenzhen University

---

## Contact

For questions about the software, models, datasets, or web server, please use the GitHub **Issues** page or contact the corresponding author listed in the manuscript.

---

## License

Please refer to the repository `LICENSE` file for reuse and redistribution terms.

