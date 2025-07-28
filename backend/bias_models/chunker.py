# chunker.py
from transformers import AutoTokenizer
from config import MAX_TOKENS

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

def chunk_text(text, max_tokens=MAX_TOKENS):
    words = text.split()
    chunks, current = [], []
    count = 0

    for word in words:
        token_len = len(tokenizer.tokenize(word))
        if count + token_len > max_tokens:
            chunks.append(" ".join(current))
            current, count = [word], token_len
        else:
            current.append(word)
            count += token_len

    if current:
        chunks.append(" ".join(current))
    return chunks
