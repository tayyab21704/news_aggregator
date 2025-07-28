# bias_model.py
# most accrate bias model

import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from config import DEVICE, HUGGINGFACE_TOKEN

# 🌐 Local directory for the model
MODEL_NAME = "premsa/political-bias-prediction-allsides-mDeBERTa"
LOCAL_MODEL_PATH = "./models/premsa_mdeberta_bias_model"

# 🔐 Download if not available
def download_bias_model():
    if not os.path.exists(LOCAL_MODEL_PATH):
        print("⬇️ Downloading bias model with authentication...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, 
            use_auth_token=HUGGINGFACE_TOKEN
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, 
            use_auth_token=HUGGINGFACE_TOKEN
        )
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
        tokenizer.save_pretrained(LOCAL_MODEL_PATH)
        model.save_pretrained(LOCAL_MODEL_PATH)
        print("✅ Model downloaded and saved locally.")
    else:
        print("📁 Bias model already exists locally.")

# 🧠 Load bias model
def load_bias_model():
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)
    return tokenizer, model.to(DEVICE)

# ⚖️ Bias analysis
def analyze_bias(chunks, sentiment_results=None):
    download_bias_model()
    tokenizer, model = load_bias_model()

    print("🔍 Evaluating political leaning on text chunks...")

    # Labels based on the model documentation
    labels = ["left", "lean left", "center", "lean right", "right"]
    label_map = {0: "left", 1: "lean left", 2: "center", 3: "lean right", 4: "right"}

    results = []
    bias_counts = {label: 0 for label in labels}

    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().numpy()[0]
        pred_label = label_map[scores.argmax()]
        results.append({
            "chunk": chunk,
            "bias": pred_label,
            "confidence": float(scores.max())
        })
        bias_counts[pred_label] += 1

    # 🧠 Determine overall bias
    bias_overall = max(bias_counts, key=bias_counts.get)
    remarks = f"Text shows a tendency towards **{bias_overall.upper()}** leaning."

    # 📌 Highlight biased chunks
    highlighted_bias_lines = [
        f"[{r['bias'].upper()} | {round(r['confidence']*100, 1)}%] {r['chunk'][:100]}..."
        for r in results if r['bias'] not in ["center"]
    ]

    return {
        "bias_overall": bias_overall,
        "remarks": remarks,
        "highlighted_bias_lines": highlighted_bias_lines
    }