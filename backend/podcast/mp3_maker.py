import requests
import os
from dotenv import load_dotenv
from pydub import AudioSegment

# --------- Load API KEY from rqmnts.env ---------
load_dotenv("rqmnts.env")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ ELEVENLABS_API_KEY not found in rqmnts.env")

# --------- Configuration ---------
MALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"    # Roger
FEMALE_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
SCRIPT_FILE = "podcast_script.txt"
OUTPUT_FILE = "final_podcast.mp3"

# --------- TTS FUNCTION ---------
def text_to_speech(text, voice_id, index):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        file_name = f"segment_{index}.mp3"
        with open(file_name, "wb") as audio_file:
            audio_file.write(response.content)
        print(f"🎧 Saved: {file_name}")
        return True
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")
        return False

# --------- SEGMENT CREATION ---------
def create_podcast_segments(script_path=SCRIPT_FILE):
    voice_ids = [MALE_VOICE_ID, FEMALE_VOICE_ID]
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            lines = [
                line.strip() for line in f
                if line.strip() and (line.startswith("Ryan:") or line.startswith("Sarah:"))
            ]
    except FileNotFoundError:
        print(f"❌ Script file '{script_path}' not found.")
        return False

    print(f"🔄 Generating {len(lines)} segments...")
    for i, line in enumerate(lines):
        try:
            _, text = line.split(":", 1)
        except ValueError:
            print(f"⚠️ Skipped invalid line: {line}")
            continue
        voice_id = voice_ids[i % 2]
        if not text_to_speech(text.strip(), voice_id, i):
            return False

    print("✅ All audio segments generated.")
    return True

# --------- AUDIO MERGE ---------
def merge_segments(output_filename=OUTPUT_FILE):
    segments = []
    i = 0

    while True:
        file_name = f"segment_{i}.mp3"
        if not os.path.exists(file_name):
            break
        segments.append(AudioSegment.from_mp3(file_name))
        i += 1

    if not segments:
        print("❌ No audio segments found.")
        return False

    final = sum(segments)
    final.export(output_filename, format="mp3")
    print(f"✅ Final podcast saved as {output_filename}")

    # Cleanup
    for j in range(i):
        os.remove(f"segment_{j}.mp3")

    return True

# --------- MAIN EXECUTION ---------
def create_podcast():
    if create_podcast_segments():
        merge_segments()

if __name__ == "__main__":
    create_podcast()
