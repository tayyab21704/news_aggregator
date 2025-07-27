# main.py

import sys, os
from dotenv import load_dotenv

# Ensure project root is on sys.path
top = os.path.dirname(__file__)
sys.path.insert(0, top)

# Load environment variables
load_dotenv(dotenv_path="rqmnts.env")
raw_gemini = os.getenv("GEMINI_API_KEY") or ""
raw_eleven = os.getenv("ELEVENLABS_API_KEY") or ""

# Strip any quotes
GEMINI_API_KEY = raw_gemini.strip('"').strip("'")
ELEVENLABS_API_KEY = raw_eleven.strip('"').strip("'")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found or empty")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("❌ ELEVENLABS_API_KEY not found or empty")

# Configure modules that need the keys
from old.generate_script import load_api_key, generate_full_podcast_script
from old.audio_generator import create_podcast


def main():
    print("▶️ Starting podcast generation flow...\n")

    print("1️⃣ Generating podcast script…")
    script_text = generate_full_podcast_script()  # writes podcast_script.txt
    print("   ✅ Script ready: podcast_script.txt\n")

    print("2️⃣ Converting script to audio…")
    if create_podcast(script_text, output_filename="final_podcast.mp3"):
        print("   ✅ Audio ready: final_podcast.mp3")
    else:
        print("   ❌ Audio generation failed.")

    print("\n🎉 All done! Check your project folder for output files.")

if __name__ == "__main__":
    main()
