#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask application: A Two-Stage Framework for Generalized Eukaryotic
Promoter Prediction and Promoter Strength Classification.

Stage 1: CNN-BiLSTM  -> promoter vs non-promoter
Stage 2: species-specific CNN / XGBoost -> strong vs weak promoter
"""

import io
import os
import uuid

from Bio import SeqIO
from flask import Flask, render_template, request, send_from_directory, url_for

from config import config
from model_utils import predict_promoter_pipeline, load_stage1_model

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

# Load Stage 1 model once at startup. Stage 2 models are loaded lazily
# and cached the first time they are needed (see model_utils.load_stage2_model).
print("Starting Promoter Prediction server, loading Stage 1 model...")
stage1_model = load_stage1_model()
print("Ready.")


# =========================================================
# Helpers
# =========================================================


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def parse_input_sequences(text_input, uploaded_file):
    """
    Build a list of (header, sequence) tuples from pasted text and/or an
    uploaded .txt / .fasta file. Supports multi-FASTA, single raw sequences,
    and plain text files with one sequence per line.
    """
    records = []

    def parse_block(raw_text, prefix):
        raw_text = raw_text.strip()
        if not raw_text:
            return []
        block_records = []
        if raw_text.startswith(">"):
            handle = io.StringIO(raw_text)
            for rec in SeqIO.parse(handle, "fasta"):
                block_records.append((rec.description or rec.id, str(rec.seq)))
        if not block_records:
            # Not FASTA formatted (or parsing found nothing) - treat each
            # non-empty line as its own sequence.
            lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
            for i, ln in enumerate(lines, start=1):
                block_records.append((f"{prefix}_{i}", ln))
        return block_records

    if text_input and text_input.strip():
        records.extend(parse_block(text_input, "Pasted_Sequence"))

    if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        records.extend(parse_block(content, "Uploaded_Sequence"))

    return records


def build_result_summary_html(header, result):
    """Compose the HTML snippet shown for one sequence in the results panel.
    Shows classification probabilities only, no raw sequence text."""
    status_lines = [f"<strong>{header}</strong><br>"]
    status_lines.append(
        f"Promoter probability: {result['promoter_probability']:.4f} "
        f"({'Promoter' if result['is_promoter'] else 'Non-promoter'})"
    )

    if result["is_promoter"]:
        if result["species"] == "Unknown":
            status_lines.append(
                f'<br><span class="unknown-tag">Species: Unknown</span> '
                f"(below confidence threshold) &mdash; closest match "
                f"{result['strength']} (prob: {result['strength_probability']:.4f})"
            )
        elif result["species"]:
            status_lines.append(
                f'<br><span class="highlight">Species: {result["species"]}</span> '
                f"&mdash; Strength: {result['strength']} "
                f"(prob: {result['strength_probability']:.4f})"
            )

    return "".join(status_lines)


def save_promoter_fasta(promoter_records, out_path):
    with open(out_path, "w") as f:
        for header, seq in promoter_records:
            f.write(f">{header}\n{seq}\n")


# =========================================================
# Routes
# =========================================================


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    text_input = request.form.get("sequence", "")
    uploaded_file = request.files.get("file")
    threshold = float(request.form.get("threshold", 0.5) or 0.5)

    records = parse_input_sequences(text_input, uploaded_file)

    if not records:
        return render_template(
            "index.html",
            error="No valid sequence was provided. Paste a sequence or upload a .txt / .fasta file.",
        )

    results = []
    promoters_count = 0
    non_promoters_count = 0
    promoter_records = []
    species_counts = {
        species: {"Strong": 0, "Weak": 0} for species in config.STAGE2_MODELS.keys()
    }
    unknown_counts = {"Strong": 0, "Weak": 0}

    for header, raw_seq in records:
        result, best_species = predict_promoter_pipeline(raw_seq, stage1_model, threshold)

        if len(result["sequence"]) == 0:
            # No valid bases in this entry, skip it from counts but still show a message.
            summary_html = f"<strong>{header}</strong><br>{result['message']}"
            results.append((header, summary_html, result))
            continue

        summary_html = build_result_summary_html(header, result)
        results.append((header, summary_html, result))

        if result["is_promoter"]:
            promoters_count += 1
            promoter_records.append((header, result["sequence"]))
            strength = result["strength"] if result["strength"] in ("Strong", "Weak") else None
            if result["species"] == "Unknown":
                if strength:
                    unknown_counts[strength] += 1
            elif result["species"] in species_counts and strength:
                species_counts[result["species"]][strength] += 1
        else:
            non_promoters_count += 1

    # Only keep species that were actually detected, in descending order of total count
    species_breakdown = [
        (species, counts["Strong"], counts["Weak"], counts["Strong"] + counts["Weak"])
        for species, counts in species_counts.items()
        if counts["Strong"] + counts["Weak"] > 0
    ]
    species_breakdown.sort(key=lambda row: row[3], reverse=True)
    unknown_species_count = unknown_counts["Strong"] + unknown_counts["Weak"]

    # Promoter subsequences FASTA for download
    promoter_subsequences_file = None
    if promoter_records:
        fasta_filename = f"promoter_subsequences_{uuid.uuid4().hex}.fasta"
        fasta_path = os.path.join(config.OUTPUT_FOLDER, fasta_filename)
        save_promoter_fasta(promoter_records, fasta_path)
        promoter_subsequences_file = fasta_filename

    return render_template(
        "index.html",
        results=results,
        promoters_count=promoters_count,
        non_promoters_count=non_promoters_count,
        species_breakdown=species_breakdown,
        unknown_species_count=unknown_species_count,
        unknown_strong=unknown_counts["Strong"],
        unknown_weak=unknown_counts["Weak"],
        promoter_subsequences_file=promoter_subsequences_file,
    )


@app.route("/download_promoter_subsequences")
def download_promoter_subsequences():
    filename = request.args.get("file")
    if not filename:
        return "No file specified.", 400
    return send_from_directory(config.OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
