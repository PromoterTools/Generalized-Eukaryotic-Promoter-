# PromoterNet

## A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification

**PromoterNet** is a two-stage computational framework for:

1. **Generalized eukaryotic promoter recognition**, and  
2. **Species-specific CAGE-derived promoter activity classification** for promoter-positive sequences.

Stage 1 uses a CNN-BiLSTM model with self-attention to classify a candidate DNA window as promoter or non-promoter. Stage 2 applies a species-specific CNN or XGBoost model to classify promoter-positive sequences into upper- and lower-activity groups defined from FANTOM5 CAGE measurements.

The project also provides attention-based sequence interpretation, surrogate-CNN SHAP analysis, trained model files, processed test data, and an interactive Flask web server.

![Graphical abstract](Graphical%20abstract.jpg)

---

## Public resources

- **GitHub repository:** https://github.com/ShujaatMuhammad/PromoterNet
- **Web server:** https://promoter-prediction-app.onrender.com/

> The public web server may require a short cold-start period after inactivity before the interface becomes available.

---

## Framework overview

### Stage 1 — Promoter vs non-promoter

PromoterNet evaluates a **300-bp DNA sequence window spanning −249 to +50 bp relative to a putative transcription start site (TSS)**.

The Stage 1 model was developed using promoter sequences from 15 eukaryotic species together with species-matched GC-balanced non-promoter sequences. *Drosophila melanogaster* was withheld from model development and used for independent cross-species evaluation.

### Stage 2 — Species-specific promoter activity

Promoter-positive sequences can be passed to Stage 2 after the user selects the **known target species**.

Supported Stage 2 species are:

| Species | Model |
|---|---|
| Human | CNN |
| Mouse | XGBoost |
| Rat | CNN |
| Dog | CNN |
| Chicken | CNN |
| Rhesus macaque | CNN |

Within each species, FANTOM5 CAGE activity was used to define:

- **Strong / high activity:** upper quartile
- **Weak / low activity:** lower quartile

The middle 50% of promoters was excluded from binary Stage 2 training.

> **Important:** PromoterNet does not infer species identity by comparing confidence scores from independently trained Stage 2 models. The target species is supplied by the user.

---

## Scope and input requirement

PromoterNet is a **candidate-window classifier**, not a genome-wide promoter scanner.

The released models are designed for **300-bp TSS-centered windows (−249 to +50 bp)**. Arbitrary-length genomic regions must first be converted into appropriate 300-bp candidate windows before prediction.

The Stage 2 labels represent **relative CAGE-derived promoter activity within each species** and should not be interpreted as universal, tissue-independent intrinsic promoter strength.

---

## Key results

### Stage 1 independent evaluation

| Metric | Value |
|---|---:|
| Accuracy | 0.9489 |
| F1-score | 0.958 |
| ROC-AUC | 0.9742 |
| PR-AUC | 0.9846 |

### Stage 1 five-fold cross-validation

| Metric | Mean ± SD |
|---|---:|
| Accuracy | 0.9436 ± 0.0017 |
| F1-score | 0.9536 ± 0.0013 |
| ROC-AUC | 0.9727 ± 0.0020 |

### Completely withheld *Drosophila melanogaster*

The independent evaluation used:

- 16,972 promoter sequences
- 16,972 GC-matched non-promoter sequences
- 33,944 total sequences
- Overall binary accuracy: **94.8%**

### Stage 2 best species-specific ROC-AUC

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

The pooled experiment is reported as a baseline rather than a strict architecture-matched ablation.

---

## Repository contents

The repository contains the deployed Flask application, model configuration/utilities, dependency specification, processed test data, trained model files, and manuscript-related resources.

Typical top-level files include:

```text
README.md
app.py
config.py
model_utils.py
requirements.txt
environment.yml
Dockerfile
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
```

---

## Installation

### Option 1 — Python virtual environment

Clone the repository:

```bash
git clone https://github.com/ShujaatMuhammad/PromoterNet.git
cd PromoterNet
```

Create and activate a virtual environment.

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

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

```bash
git clone https://github.com/ShujaatMuhammad/PromoterNet.git
cd PromoterNet
conda env create -f environment.yml
conda activate promoternet
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### Option 3 — Docker

```bash
git clone https://github.com/ShujaatMuhammad/PromoterNet.git
cd PromoterNet
docker build -t promoternet .
docker run --rm -p 5000:5000 promoternet python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Web-server tutorial

### 1. Prepare input

PromoterNet accepts:

- a single 300-bp DNA sequence,
- a multi-FASTA block,
- a `.txt`, `.fasta`, `.fa`, or `.fna` file containing one or more sequences.

Each sequence should contain **300 nucleotides**.

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

Only the corresponding species-specific Stage 2 model is used for the selected species.

### 4. Run prediction

Click **Predict**.

The interface reports:

- Stage 1 promoter probability,
- promoter/non-promoter classification,
- species-specific Stage 2 activity classification for promoter-positive inputs,
- summary statistics and visualizations.

### 5. Download outputs

Available outputs include:

- predicted promoter sequences in FASTA format,
- generated result charts,
- per-sequence prediction information.

Use **Reset** to clear the current analysis and begin a new prediction.

---

## Example FASTA input

```text
>example_sequence
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
...
```

The complete sequence should contain **300 bp**.

---

## Data construction

### Stage 1

Promoter sequences were obtained from **EPDnew**. Species-matched non-promoter sequences were constructed with GC-content matching, and sequence redundancy was reduced before model development.

Fifteen species were used for Stage 1 development. *D. melanogaster* was excluded from development and retained for independent cross-species evaluation.

### Stage 2

Species-specific promoter activity labels were derived from **FANTOM5 CAGE** data.

Within each species:

- the upper activity quartile was assigned to the strong/high-activity group,
- the lower activity quartile was assigned to the weak/low-activity group,
- the middle 50% was excluded from binary Stage 2 training.

Detailed sample counts, genome-build information, CAGE aggregation procedures, model parameters, validation analyses, and statistical tests are documented in the manuscript and Supporting Information.

---

## Model interpretation

### Attention analysis

Attention weights from the primary Stage 1 CNN-BiLSTM model are used to examine promoter-associated sequence regions and motifs.

### Surrogate-CNN SHAP analysis

SHAP analysis is performed using a **surrogate one-hot CNN**, not directly on the primary CNN-BiLSTM model.

Therefore, SHAP-associated k-mers and nucleotide-level contributions are interpreted as **complementary model-associated evidence**, not as direct attribution of the primary CNN-BiLSTM.

---

## Reproducible web-server launch

After cloning and installing the dependencies:

```bash
git clone https://github.com/ShujaatMuhammad/PromoterNet.git
cd PromoterNet
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The released independent test split is provided as:

```text
independent_test_split.csv
```

---

## Limitations

PromoterNet should be interpreted within the scope of the released benchmark.

- The models classify predefined **300-bp TSS-centered windows** rather than arbitrary genomic regions.
- Genome-wide promoter discovery would require candidate-window generation or tiling before classification.
- Stage 2 activity labels are based on upper/lower FANTOM5 CAGE quartiles within individual species.
- The middle 50% excluded from Stage 2 training is not a separately trained third class.
- CAGE activity is tissue- and condition-dependent.
- Stage 2 performance depends on the amount and composition of species-specific labeled data.
- SHAP interpretation is based on a surrogate CNN rather than direct SHAP attribution of the primary CNN-BiLSTM.
- The pooled Stage 2 experiment is a baseline rather than a strict architecture-controlled ablation.

---

## Citation

If you use PromoterNet, please cite the associated manuscript:

> Muhammad Shujaat and Shi-Qing Mao. **A Two-Stage Framework for Generalized Eukaryotic Promoter Prediction and Promoter Strength Classification.**

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
