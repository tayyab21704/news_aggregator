# services/audio_generator.py
import os
from pydub import AudioSegment
# from pydub.playback import play # For local testing, requires ffplay
from typing import List, Dict
from io import BytesIO # Needed to read audio bytes into pydub

# --- CORRECTED IMPORTS FOR ELEVEN LABS (for v2.8.0) ---
from elevenlabs import Voice, VoiceSettings # Voice and VoiceSettings are still direct imports
from elevenlabs.client import ElevenLabs # ElevenLabs client is imported from elevenlabs.client
# Removed: from elevenlabs import generate # This is no longer a direct top-level import
# --- END CORRECTED IMPORTS ---

class AudioGenerator:
    def __init__(self):
        # --- Initialize ElevenLabs Client ---
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set. Cannot use ElevenLabs TTS.")
        
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

        # --- Define voices for Host A and Host B using Eleven Labs Voice IDs ---
        # IMPORTANT: Replace these with actual Voice IDs from your Eleven Labs account.
        # You can find these in your Eleven Labs dashboard under 'VoiceLab' or 'Voices'.
        # Common premade voices: Adam (EXAVoV4dpukA0UGzGwvm), Rachel (21m00Tcm4TlvDq8ikWAM), Bella (EXAVoV4dpukA0UGzGwvm)
        # Choose two distinct voices for your hosts.
        # Ensure these are voice IDs you have access to in your ElevenLabs account.
        self.voice_a_id = "EXAVoV4dpukA0UGzGwvm"  # Example: Adam (male voice)
        self.voice_b_id = "21m00Tcm4TlvDq8ikWAM"  # Example: Rachel (female voice)
        
        # Optional: You can set specific VoiceSettings for more control over stability, clarity etc.
        # For the .convert() method, if you want to apply custom settings,
        # you might need to pass a dictionary to `voice_settings` parameter.
        # self.default_voice_settings = {"stability": 0.5, "similarity_boost": 0.75}


    def _generate_speech(self, text: str, voice_id: str) -> bytes:
        """
        Generates speech bytes using the Eleven Labs API.
        Handles ElevenLabs' per-generation character limit.
        """
        # Eleven Labs free tier has a per-generation character limit (e.g., 2500 chars).
        # While LLM output for a single line should generally be within this,
        # it's good to be aware or add explicit chunking for very long lines if needed.
        if len(text) > 2500:
            print(f"WARNING: Text segment exceeds ElevenLabs 2500 character recommended limit ({len(text)}). This line may be truncated or cause an error.")
            # For robustness, you might implement a simple text splitter here
            # and call generate multiple times, then stitch. For hackathon,
            # assume LLM generates reasonable line lengths.

        try:
            # The .convert() method returns a bytes object directly, not an iterator
            audio_bytes = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2", # Or "eleven_monolingual_v1" if only English
                output_format="mp3_44100_128", # Example format: MP3, 44.1kHz, 128kbps
                # If you uncommented self.default_voice_settings in __init__, you could pass it here:
                # voice_settings=self.default_voice_settings
            )
            return audio_bytes
        except Exception as e:
            print(f"ERROR: ElevenLabs speech generation failed for text '{text[:50]}...': {e}")
            return b'' # Return empty bytes on error


    def generate_podcast_audio(self, script_text: str, output_filepath: str = "podcast.mp3"):
        """
        Generates a podcast audio file from a multi-speaker script using Eleven Labs.
        Assumes script_text has lines like "Host A: blabla" and "Host B: blabla".
        Includes a small silent buffer between speaker turns for natural flow.
        """
        podcast_audio = AudioSegment.empty()
        lines = script_text.strip().split('\n')

        # Add a small silent buffer between speaker turns for better separation
        silent_segment = AudioSegment.silent(duration=300) # 300 milliseconds of silence

        for line in lines:
            line = line.strip()
            speaker_text = ""
            voice_id_to_use = None

            if line.startswith("Host A:"):
                speaker_text = line[len("Host A:"):].strip()
                voice_id_to_use = self.voice_a_id
            elif line.startswith("Host B:"):
                speaker_text = line[len("Host B:"):].strip()
                voice_id_to_use = self.voice_b_id
            else:
                # Handle lines that don't fit speaker format, maybe narrator or just skip
                if line: # Only print if line is not empty
                    print(f"Skipping malformed script line or unrecognized speaker format: '{line}'")
                continue # Skip to next line if format doesn't match

            if speaker_text and voice_id_to_use:
                try:
                    audio_segment_bytes = self._generate_speech(speaker_text, voice_id_to_use)
                    
                    if audio_segment_bytes: # Only add if speech generation was successful
                        # Use a BytesIO object for pydub to read directly from memory
                        segment = AudioSegment.from_file(BytesIO(audio_segment_bytes), format="mp3")
                        podcast_audio += segment + silent_segment
                    else:
                        # Add a placeholder silence if speech generation failed
                        print(f"Adding silence for failed speech segment: '{speaker_text[:50]}...'")
                        podcast_audio += AudioSegment.silent(duration=1000) # 1 second silence for error
                except Exception as e:
                    print(f"CRITICAL ERROR processing audio segment for line '{speaker_text[:50]}...': {e}")
                    podcast_audio += AudioSegment.silent(duration=2000) # Longer silence for critical error

        if not podcast_audio.duration_seconds > 0:
            print("WARNING: No audio segments were generated. Output file might be empty.")
            # Add a default silence if no audio was generated at all
            podcast_audio = AudioSegment.silent(duration=5000) # 5 seconds of silence

        podcast_audio.export(output_filepath, format="mp3")
        print(f"Podcast generated and saved to {output_filepath}")
        return output_filepath

# Example Usage (for testing this module directly)
if __name__ == "__main__":
    # --- IMPORTANT: Ensure .env is loaded for ELEVENLABS_API_KEY, GOOGLE_API_KEY, TAVILY_API_KEY ---
    from dotenv import load_dotenv
    load_dotenv()

    # --- NEW IMPORTS FOR THE FULL PIPELINE ---
    from services.data_loader import load_articles_from_files
    from services.analysis_engine import AnalysisEngine
    from services.podcast_script_generator import PodcastScriptGenerator

    # --- Define your absolute file paths for testing ---
    # These paths correspond to your actual test files in the 'test_data' directory.
    file1path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article1_national_voice.txt"
    file2path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article2_vigilant_daily.txt"
    # If you have an article3_neutral_source.txt, define its path here as well.
    # file3path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article3_neutral_source.txt"

    # --- STEP 1: Load Articles ---
    print("\n--- STEP 1: Loading Articles for Test ---")
    podcast_articles = load_articles_from_files([file1path])
    # For a debate scenario, you'd load: load_articles_from_files([file1path, file2path])
    
    if not podcast_articles:
        print("ERROR: No articles loaded. Cannot proceed with audio generation test.")
        exit() # Exit if no articles to process

    # --- STEP 2: Analyze Articles ---
    print("\n--- STEP 2: Analyzing Articles ---")
    analysis_engine = AnalysisEngine()
    analysis_reports = []
    for article_data in podcast_articles:
        try:
            report = analysis_engine.analyze_article(article_data)
            analysis_reports.append(report)
        except Exception as e:
            print(f"ERROR: Analysis failed for article '{article_data.get('title', 'Untitled')}': {e}")
    
    if not analysis_reports:
        print("ERROR: No analysis reports generated. Cannot proceed with audio generation test.")
        exit() # Exit if no reports

    # --- STEP 3: Generate Podcast Script ---
    print("\n--- STEP 3: Generating Podcast Script ---")
    script_generator = PodcastScriptGenerator()
    generated_script = ""
    try:
        # Pass the list of analysis reports to the script generator
        generated_script = script_generator.generate_script(analysis_reports)
        if generated_script:
            print("\n--- Generated Script (Partial) ---")
            print(generated_script[:500] + "...") # Print first 500 chars of script
        else:
            print("WARNING: Script generation returned empty.")
    except Exception as e:
        print(f"ERROR: Script generation failed: {e}")

    if not generated_script:
        print("ERROR: No script generated. Cannot proceed with audio generation.")
        # Fallback to a very simple dummy script to allow audio generation to attempt
        generated_script = "Host A: Welcome. Today's news update encountered an issue. Host B: Please check back later for full details."


    # --- STEP 4: Generate Podcast Audio ---
    print("\n--- STEP 4: Generating Podcast Audio ---")
    audio_gen = AudioGenerator() 
    
    # Ensure FFmpeg is installed on your system for pydub to work
    # You can test by running 'ffmpeg -version' in your terminal.

    try:
        output_audio_file = "elevenlabs_full_pipeline_podcast.mp3"
        generated_file = audio_gen.generate_podcast_audio(generated_script, output_audio_file)
        print(f"Podcast generated and saved to: {generated_file}")
        
        # Optional: Play the generated audio locally (requires ffplay installed and in PATH)
        # from pydub.playback import play
        # print("\nPlaying generated podcast...")
        # play(AudioSegment.from_file(generated_file))
    except Exception as e:
        print(f"An error occurred during audio generation: {e}")