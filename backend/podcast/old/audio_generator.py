# audio_generator.py

import requests
import os

API_KEY = os.getenv("ELEVENLABS_API_KEY")
MALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"  # Roger
FEMALE_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

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
        print(f"Error: {response.status_code}, {response.text}")
        return False

def create_podcast_segments(lines):
    voice_ids = [MALE_VOICE_ID, FEMALE_VOICE_ID]
    for i, line in enumerate(lines):
        voice_id = voice_ids[i % 2]
        if not text_to_speech(line, voice_id, i):
            return False
    return True

def merge_segments(num_segments, output_filename="final_podcast.mp3"):
    try:
        from pydub import AudioSegment
        audio_segments = []
        for i in range(num_segments):
            file_name = f"segment_{i}.mp3"
            if os.path.exists(file_name):
                audio_segments.append(AudioSegment.from_mp3(file_name))

        if audio_segments:
            final_audio = sum(audio_segments)
            final_audio.export(output_filename, format="mp3")
            print(f"✅ Final podcast saved as {output_filename}")
            for i in range(num_segments):
                os.remove(f"segment_{i}.mp3")
            return True
        else:
            print("❌ No audio segments found.")
            return False

    except ImportError:
        print("Install pydub or try manual merge.")
        return False

def create_podcast(script_text, output_filename="final_podcast.mp3"):
    lines = [line for line in script_text.strip().split("\n") if line.startswith("Ryan:") or line.startswith("Sarah:")]
    if create_podcast_segments(lines):
        return merge_segments(len(lines), output_filename)
    return False
