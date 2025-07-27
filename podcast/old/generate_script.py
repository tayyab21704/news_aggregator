# generate_script.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables and configure Gemini API
def load_api_key(env_path="rqmnts.env"):
    load_dotenv(dotenv_path=env_path)
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found in environment file")
    genai.configure(api_key=key)

# Read input text from .txt file
def read_text_file(file_path="input.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Split text into chunks based on token count
def chunk_text(text, max_tokens=10000):
    chunks, current, count = [], "", 0
    for sentence in text.split(". "):
        tokens = len(sentence.split())
        if count + tokens <= max_tokens:
            current += sentence + ". "
            count += tokens
        else:
            chunks.append(current.strip())
            current, count = sentence + ". ", tokens
    if current:
        chunks.append(current.strip())
    return chunks

# Generate a script segment using Gemini
def generate_script_segment(text_chunk, is_last_chunk=False, previous_context=""):
    prompt = f"""
You are a professional news podcast scriptwriter.

Generate a calm, informative, and neutral-toned podcast script for two speakers, Ryan and Sarah, who discuss current events, laws, governance, technology, and crime from an unbiased but analytical viewpoint.

Instructions:
- Structure the script as a serious and insightful conversation between the two hosts.
- They must interpret the facts, bring clarity, and guide the youth on how to think critically about the topic.
- Avoid jokes, slang, or overly casual language.
- Use only these speaker tags: Ryan: and Sarah:

Context:
{previous_context}

New Content:
{text_chunk}
"""
    if is_last_chunk:
        prompt += """
At the end of the script, add a reflection segment between Ryan and Sarah where they respectfully discuss whether the news appears biased — Left, Right, or Neutral — and why.
"""
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    return response.text

# Assemble the full podcast script and save to file
def generate_full_podcast_script(input_path="input.txt", output_path="podcast_script.txt"):
    # Load and configure API
    load_api_key()

    # Read and chunk the input text
    text = read_text_file(input_path)
    chunks = chunk_text(text)
    full_script, prev = "", ""

    # Prepend intro to the first chunk
    if chunks:
        chunks[0] = "Welcome to the podcast. " + chunks[0]

    # Generate script segments
    for i, chunk in enumerate(chunks):
        is_last = (i == len(chunks) - 1)
        segment = generate_script_segment(chunk, is_last, prev)
        full_script += segment + "\n"
        prev = chunk

    # Add closing lines
    full_script += (
        "\nRyan: And that's all for today!\n"
        "Sarah: Thanks for tuning in. Stay informed, stay thoughtful.\n"
    )

    # Save the complete script to a text file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_script)
    print(f"✅ Podcast script saved to: {output_path}")
    return full_script

# Entry point when run directly
if __name__ == "__main__":
    generate_full_podcast_script()
