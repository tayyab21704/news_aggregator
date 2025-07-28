# podcast_audio_generator.py

import requests
import os
import re
from dotenv import load_dotenv

# ✅ Load API key from rqmnts.env
def load_api_key(env_path="rqmnts.env"):
    load_dotenv(dotenv_path=env_path)
    return os.getenv("ELEVENLABS_API_KEY")

# ✅ Voice IDs
MALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"   # Ryan
FEMALE_VOICE_ID = "21m00Tcm4TlvDq8ikWAM" # Sarah

# ✅ Assign speaker to voice
def get_voice_id(speaker):
    return MALE_VOICE_ID if "Ryan" in speaker else FEMALE_VOICE_ID

# ✅ Parse script into clean dialogue lines
def extract_dialogue_lines(script_text):
    pattern = r"^(Ryan|Sarah): (.+)$"
    lines = []
    for match in re.finditer(pattern, script_text, flags=re.MULTILINE):
        speaker = match.group(1)
        text = match.group(2).strip()
        lines.append((speaker, text))
    return lines

# ✅ Send text to ElevenLabs and save audio
def text_to_speech(text, voice_id, index, api_key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        file_name = f"segment_{index}.mp3"
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved segment: {file_name}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

# ✅ Main function
def generate_podcast_audio(script_file="podcast_script.txt"):
    api_key = load_api_key()
    if not api_key:
        print("❌ ElevenLabs API key not found.")
        return

    with open(script_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    dialogues = extract_dialogue_lines(script_text)
    if not dialogues:
        print("❌ No dialogue lines found in the script.")
        return

    for i, (speaker, text) in enumerate(dialogues):
        voice_id = get_voice_id(speaker)
        text_to_speech(f"{text}", voice_id, i, api_key)

    print("✅ All segments generated.")

if __name__ == "__main__":
    generate_podcast_audio()
