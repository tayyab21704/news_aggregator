# bias_model.py
# fastest results


import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from config import DEVICE, HUGGINGFACE_TOKEN

# 🌐 Model details
MODEL_NAME = "cajcodes/DistilBERT-PoliticalBias"
LOCAL_MODEL_PATH = "./models/cajcodes_distilbert_model"

# 🔽 Download the model if not already present
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

# 🧠 Load model
def load_bias_model():
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)
    return tokenizer, model.to(DEVICE)

# ⚖️ Analyze bias in text chunks
def analyze_bias(chunks, sentiment_results=None):
    download_bias_model()
    tokenizer, model = load_bias_model()

    print("🔍 Evaluating political leaning on text chunks...")

    label_map = {0: "left", 1: "center", 2: "right"}
    results = []
    bias_counts = {"left": 0, "center": 0, "right": 0}

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

    # 📈 Overall prediction
    bias_overall = max(bias_counts, key=bias_counts.get)
    remarks = f"Text shows a tendency towards **{bias_overall.upper()}** leaning."

    # 🔎 Highlight bias lines
    highlighted_bias_lines = [
        f"[{r['bias'].upper()} | {round(r['confidence']*100, 1)}%] {r['chunk'][:100]}..."
        for r in results if r['bias'] != "center"
    ]

    return {
        "bias_overall": bias_overall,
        "remarks": remarks,
        "highlighted_bias_lines": highlighted_bias_lines
    }
