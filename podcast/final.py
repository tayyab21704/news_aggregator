# needs to run this file ignore the ones in the old folder 
# make a .env file and you eleven labs and gemini api keys 
# run requirements.txt for dependencies create a virtual environment to prevent depencies issues
# test input needs to pasted inside input.txt


from script import generate_full_podcast_script
from mp3_maker import create_podcast

def main():
    print("🎙️ Generating podcast script...")
    generate_full_podcast_script(
        input_path="input.txt",         # Input news/content
        output_path="podcast_script.txt" # Output generated script
    )

    print("\n🔊 Converting script to audio...")
    create_podcast()

    print("\n✅ Podcast generation complete.")

if __name__ == "__main__":
    main()
