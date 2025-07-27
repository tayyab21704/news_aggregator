# generate_script.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ Load custom .env file for Gemini API Key
def load_api_key(env_path="rqmnts.env"):
    load_dotenv(dotenv_path=env_path)
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found in environment file")
    genai.configure(api_key=key)

# --------------------- Read Input from .txt ---------------------
def read_input_file(file_path="input.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# --------------------- TEXT CHUNKING ---------------------
def chunk_text(text, target_input_tokens=10000):
    text_chunks = []
    current_chunk = ""
    current_chunk_tokens = 0
    for sentence in text.split(". "):
        sentence_tokens = len(sentence.split())
        if current_chunk_tokens + sentence_tokens <= target_input_tokens:
            current_chunk += sentence + ". "
            current_chunk_tokens += sentence_tokens
        else:
            text_chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
            current_chunk_tokens = sentence_tokens
    if current_chunk:
        text_chunks.append(current_chunk.strip())
    return text_chunks

# ------------------ SCRIPT GENERATION -------------------
def generate_script_segment(text_chunk, previous_context="", is_last=False):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
You are a professional news podcast scriptwriter.

Generate a calm, informative, and neutral-toned podcast script for two speakers, Ryan and Sarah, who discuss current events, laws, governance, technology, and crime from an unbiased but analytical viewpoint.

Instructions:
- Structure the script as a serious and insightful conversation.
- Interpret facts, guide critical thinking.
- Avoid jokes, slang, overly casual language.
- Use only speaker tags: Ryan: and Sarah:
At the start, provide at least three exchanges between Ryan and Sarah to introduce the episode and topic. Throughout the script segments, generate extended dialogue covering detailed facts, expert commentary, and data (e.g., figures, quotes). At the end, include three reflective closing exchanges summarizing findings and offering youth guidance. Aim for maximum length and insight while preserving a professional and neutral tone.

Incorporate emotional expressions like:
- Surprise: "Whoa!", "No way!", "Seriously?"
- Sadness: "That's heartbreaking.", "I can’t believe it..."
- Laughter: "Haha!", "That’s hilarious!"
- Suspense: "...and then it stopped.", "Everything went silent."
- Calm: "Let’s take a breath here.", "It’s going to be alright."

Ensure the emotional interjections are naturally blended into the flow.
Context:
{previous_context}

New Content:
{text_chunk}
"""
    if is_last:
        prompt += """
At the end, include a reflection segment where Ryan and Sarah discuss whether the news appears Left, Right, or Neutral and why.
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------- FULL SCRIPT ASSEMBLY -------------------
def generate_full_podcast_script(input_path="input.txt", output_path="podcast_script.txt"):
    # Load API and input text
    load_api_key()
    text = read_input_file(input_path)

    # Chunk text
    chunks = chunk_text(text)
    full_script = ""
    previous_context = ""

    # Add intro to first chunk
    if chunks:
        chunks[0] = "Welcome to the podcast. " + chunks[0]

    # Generate segments
    for i, chunk in enumerate(chunks):
        is_last = (i == len(chunks) - 1)
        segment = generate_script_segment(chunk, previous_context, is_last)
        full_script += segment + "\n"
        previous_context = chunk

    # Closing lines
    full_script += (
        "\nRyan: And that's all for today!\n"
        "Sarah: Thanks for tuning in. Stay informed, stay thoughtful.\n"
    )

    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_script)
    print(f"✅ Podcast script saved to: {output_path}")

    # ✅ Also save a copy in a readable location for review
    with open("script_output_backup.txt", "w", encoding="utf-8") as backup:
        backup.write(full_script)
    print("📝 Script also backed up to script_output_backup.txt")

    return full_script

# Run when executed directly
if __name__ == "__main__":
    generate_full_podcast_script()