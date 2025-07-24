# podcast_main.py
import os
import sys
from dotenv import load_dotenv

load_dotenv() # This loads the variables from your .env file into os.environ

# Add the 'services' directory to Python's path so you can import from it
# This is a common pattern for running a script at the root that imports from subdirectories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

# --- CORRECTED IMPORTS ---
from services.analysis_engine import AnalysisEngine
from services.podcast_script_generator import PodcastScriptGenerator
from services.audio_generator import AudioGenerator
from services.data_loader import load_articles_from_files # Now importing the new function
from typing import List, Dict, Any

class PodcastService:
    def __init__(self):
        # Initialize all the service components
        self.analysis_engine = AnalysisEngine()
        self.script_generator = PodcastScriptGenerator()
        self.audio_generator = AudioGenerator()

    def generate_full_podcast(self, article_filepaths: List[str], output_filename: str = "generated_podcast.mp3") -> str:
        """
        Generates a complete bias-aware, fact-checked, conversational podcast.
        Loads article content directly from provided file paths.
        :param article_filepaths: A list of absolute file paths to the .txt article data.
        :param output_filename: The desired name for the output MP3 file.
        :return: Path to the generated MP3 file.
        """
        # Step 0: Load the article data directly from the provided file paths
        print("\n--- [ORCHESTRATOR] Loading article data from files... ---")
        articles_input = load_articles_from_files(article_filepaths)
        
        if not articles_input:
            raise ValueError(f"No article input found for the given file paths (check files in {article_filepaths}).")

        print("\n--- Beginning Podcast Generation Process ---")

        # Step 1: Analyze each article for bias and claims
        all_analysis_reports = []
        for article_data in articles_input:
            print(f"\n[ORCHESTRATOR] Analyzing article: {article_data['title']} from {article_data['source_name']}")
            report = self.analysis_engine.analyze_article(article_data)
            all_analysis_reports.append(report)
        
        # Step 2: Generate the conversational script based on all analysis reports
        print("\n[ORCHESTRATOR] Generating podcast script...")
        podcast_script = self.script_generator.generate_script(all_analysis_reports)
        print("\n[ORCHESTRATOR] Script Generated. First 500 chars:\n", podcast_script[:500])
        
        # Step 3: Generate audio from the script
        print("\n[ORCHESTRATOR] Generating audio from script...")
        final_audio_path = self.audio_generator.generate_podcast_audio(podcast_script, output_filename)
        
        print(f"\n--- Podcast Generation Complete: {final_audio_path} ---")
        return final_audio_path

if __name__ == "__main__":
    # Ensure all necessary API keys and environmental variables are set up
    # (e.g., GOOGLE_API_KEY, TAVILY_API_KEY, ELEVENLABS_API_KEY)
    # The load_dotenv() at the top of the file handles this from your .env file.
    
    service = PodcastService()
    
    # --- Define your absolute file paths ---
    # IMPORTANT: Ensure these paths are correct for your system.
    file1path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article1_national_voice.txt"
    file2path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article2_vigilant_daily.txt"
    # If you have an article3_neutral_source.txt, define its path here as well.
    # file3path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article3_neutral_source.txt"

    # --- Test Cases ---

    # Test Case 1: Podcast from a single article file
    print("\n\n--- TEST CASE 1: Generating Podcast from Single Article File ---")
    try:
        podcast_file_single = service.generate_full_podcast(
            [file1path], # Pass the list of file paths
            "single_article_podcast.mp3"
        )
        print(f"Single Article Podcast generated at: {podcast_file_single}")
    except Exception as e:
        print(f"Error in single article podcast generation: {e}")

    # Test Case 2: Podcast from two contrasting article files (for a debate)
    print("\n\n--- TEST CASE 2: Generating Podcast from Two Contrasting Article Files ---")
    try:
        podcast_file_debate = service.generate_full_podcast(
            [file1path, file2path], # Pass the list of file paths
            "debate_podcast.mp3"
        )
        print(f"Debate Podcast generated at: {podcast_file_debate}")
    except Exception as e:
        print(f"Error in debate podcast generation: {e}")

    # You can also add code here to play the generated audio for local testing (requires ffplay)
    # from pydub import AudioSegment
    # from pydub.playback import play
    # if os.path.exists("debate_podcast.mp3"):
    #     print("\nPlaying debate podcast...")
    #     try:
    #         play(AudioSegment.from_mp3("debate_podcast.mp3"))
    #     except Exception as play_err:
    #         print(f"Error playing audio (ensure ffplay is installed and in PATH): {play_err}")