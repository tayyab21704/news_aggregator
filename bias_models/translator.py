# translator.py

from transformers import pipeline, AutoTokenizer
from config import TRANSLATOR_MODEL, MAX_TOKENS
import torch

# 🛠 Load translation pipeline locally
translator = pipeline(
    "translation",
    model=TRANSLATOR_MODEL,
    tokenizer=TRANSLATOR_MODEL,
    device=0 if torch.cuda.is_available() else -1
)

# Load tokenizer to chunk
tokenizer = AutoTokenizer.from_pretrained(TRANSLATOR_MODEL)

def chunk_text_for_translation(text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
    """
    Splits text into sub-strings of <= max_tokens tokens for translation.
    """
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        tok_slice = tokens[i : i + max_tokens]
        chunk = tokenizer.convert_tokens_to_string(tok_slice)
        chunks.append(chunk)
    return chunks

def translate_chunks(chunks: list[str]) -> list[str]:
    """
    Translates a list of English/Hindi text chunks to English locally.
    """
    translated = []
    for idx, chunk in enumerate(chunks):
        print(f"🌐 Translating chunk {idx+1}/{len(chunks)} locally...")
        try:
            # Use pipeline to translate
            out = translator(chunk, max_length=1000)[0]
            translated.append(out["translation_text"])
        except Exception as e:
            print(f"❌ Translation failed for chunk {idx}: {e}")
            translated.append(chunk)
    return translated
