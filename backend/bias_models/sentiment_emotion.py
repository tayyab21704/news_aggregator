# sentiment_emotion.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from config import SENTIMENT_MODEL, MAX_TOKENS
import torch

# 👟 Load tokenizer & model once
tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)

# 🚀 Build a pipeline that returns all scores
emotion_pipe = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=True,
    device=0 if torch.cuda.is_available() else -1
)

def chunk_text(text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
    """
    Splits `text` into chunks of <= max_tokens WordPiece tokens.
    """
    # Tokenize entire text to tokens
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        token_slice = tokens[i : i + max_tokens]
        chunk = tokenizer.convert_tokens_to_string(token_slice)
        chunks.append(chunk)
    return chunks

def analyze_sentiment_emotion(text: str) -> list[dict]:
    """
    Analyzes emotions chunk by chunk and returns top emotion + score.
    """
    results = []
    # 1️⃣ Chunk input safely
    chunks = chunk_text(text)

    # 2️⃣ Process each chunk
    for idx, chunk in enumerate(chunks):
        try:
            # Returns list of lists: [[{label,score},...]]
            all_scores = emotion_pipe(chunk)[0]
            # Pick the label with highest score
            top = max(all_scores, key=lambda x: x["score"])
            results.append({
                "chunk_index": idx,
                "emotion": top["label"],
                "confidence": round(top["score"], 4)
            })
        except Exception as e:
            print(f"❌ Error on chunk {idx}: {e}")
            results.append({
                "chunk_index": idx,
                "emotion": "error",
                "confidence": 0.0
            })

    return results
