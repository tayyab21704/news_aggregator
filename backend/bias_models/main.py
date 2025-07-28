# main.py

import os
from config import DEVICE
from chunker import chunk_text
from sentiment_emotion import analyze_sentiment_emotion
from translator import translate_chunks
from checked.bias_model1 import analyze_bias
from language_utils import detect_language
from utils import read_input_text, format_output

print(f"Device set to use {DEVICE}")
print("🚀 Bias & Sentiment Detection Started")

def main():
    # Step 1: Read input text
    input_text = read_input_text("input.txt")

    # Step 2: Chunk input into 500-token blocks
    chunks = chunk_text(input_text)

    # Step 3: Sentiment analysis on original chunks
    print("🧠 Performing sentiment analysis...")
    sentiment_results = analyze_sentiment_emotion(input_text)

    # Step 4: Detect language
    lang = detect_language(input_text)
    print(f"🌐 Detected Language: {lang}")

    # Step 5: Translate only if not English
    if lang.lower() != "en":
        print("🌍 Translating chunks to English...")
        translated_chunks = translate_chunks(chunks, source_lang=lang)
    else:
        translated_chunks = chunks  # already in English

    # Step 6: Bias analysis on translated chunks
    print("⚖️ Analyzing bias...")
    bias_result = analyze_bias(translated_chunks, sentiment_results)

    # Step 7: Output formatted results
    final_output = {
        "bias_overall": bias_result["bias_overall"],
        "tone_overall": "based on sentiment only",  # If tone model removed
        "remarks": bias_result["remarks"],
        "highlighted_bias_lines": bias_result["highlighted_bias_lines"],
        "highlighted_sentiments": sentiment_results
    }

    print("\n📊 Final Output:\n")
    print(format_output(final_output, sentiment_results))


if __name__ == "__main__":
    main()
