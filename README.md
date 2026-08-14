# Two-Stage Eukaryotic Promoter Prediction — Flask App

Web interface for the two-stage promoter prediction pipeline:

- **Stage 1**: CNN-BiLSTM with self-attention, promoter vs non-promoter.
- **Stage 2**: species-specific CNN or XGBoost model, strong vs weak promoter, tried across all configured species (Human, Mouse, Rat, Dog, Chicken, Macaque) with the best-confidence match reported. Matches below the confidence threshold are labeled "Unknown".

## Project structure

```
promoter_prediction_app/
├── app.py                  Flask routes (/, /predict, /download_promoter_subsequences)
├── model_utils.py          Model architectures + prediction pipeline (from your script)
├── config.py                Model paths and hyperparameters
├── requirements.txt
├── templates/
│   └── index.html           Web form + results page (new teal/indigo theme)
├── static/
│   ├── css/style.css        Stylesheet
│   └── plots/                Nucleotide composition plots (generated per request)
├── uploads/                  Temp storage for uploaded files (currently unused by disk, kept for future use)
└── outputs/                  Generated promoter-subsequence FASTA files, served for download
```

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   If you have a CUDA GPU, install the matching `torch` build from
   https://pytorch.org/get-started/locally/ instead of the default CPU wheel.

2. Open `config.py` and confirm the model paths match your machine:

   - `STAGE1_MODEL_PATH`
   - `STAGE2_MODELS["Human"]["path"]`, `["Mouse"]["path"]`, etc.

   Species without a checkpoint on disk are simply skipped at prediction time
   (no error), so you can run with a subset of species models present.

3. Run the app:

   ```bash
   python app.py
   ```

   The app starts on `http://0.0.0.0:5000` and loads the Stage 1 model once
   at startup. Stage 2 species models are loaded lazily, the first time a
   promoter sequence needs to be classified, and then cached in memory.

## Using the app

1. Paste a single DNA sequence or a multi-FASTA block into the text box, and/or upload a `.txt` / `.fasta` file.
2. Optionally adjust the Stage 1 promoter probability threshold (default 0.5).
3. Click **Predict**. The results panel shows, for each sequence:
   - Stage 1 promoter probability and call.
   - If predicted as a promoter: best-matching species, strength (Strong/Weak), and probability, or "Unknown" if below the confidence threshold.
4. A doughnut chart summarizes the promoter / non-promoter split, and a bar chart compares average nucleotide composition between the two groups.
5. If any sequences were classified as promoters, a FASTA file of those sequences is available for download.

## Notes

- Non-ACGT characters (other than `N`, which is mapped to `A`) are stripped from input sequences before prediction.
- `SPECIES_CONFIDENCE_THRESHOLD` in `config.py` controls when a promoter is reported as "Unknown" species rather than forced into the closest match (default 0.55).
- For production deployment, run behind a WSGI server such as `gunicorn` rather than the Flask development server, and set `debug=False` in `app.py`.
