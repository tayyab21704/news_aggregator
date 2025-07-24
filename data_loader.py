# services/data_loader.py
import os
import datetime
from typing import Dict, Any, List

# No longer need TEST_DATA_DIR global if providing full paths directly
# TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data')

def _read_text_file(filepath: str) -> str:
    """Helper function to read content from a specified text file (full path expected)."""
    print(f"Attempting to read file: {filepath}") # Added for better debugging
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}. Please ensure the file exists and the path is correct.")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"ERROR: Could not read file {filepath}: {e}")
        return ""

def _infer_metadata_from_filename(filepath: str) -> Dict[str, str]:
    """
    Infers basic metadata (title, source_name, publish_date) from the filename.
    Assumes filepath is the full path.
    """
    filename = os.path.basename(filepath)
    name_parts = filename.replace('.txt', '').split('_')

    # Basic inference for title
    title = filename.replace('.txt', '').replace('_', ' ').title() # Capitalize words

    # Infer source name: e.g., "article1_national_voice.txt" -> "National Voice"
    source_name = "Generic Source"
    if len(name_parts) >= 2:
        # Assuming format like articleX_source_name.txt
        # Join parts after "articleX" to form source name
        source_name_parts = name_parts[1:]
        source_name = " ".join(part.capitalize() for part in source_name_parts)
    elif len(name_parts) == 1:
        source_name = name_parts[0].capitalize() + " News"

    # Get file modification date as a proxy for publish_date
    try:
        mod_timestamp = os.path.getmtime(filepath)
        publish_date = datetime.datetime.fromtimestamp(mod_timestamp).strftime("%Y-%m-%d")
    except Exception:
        publish_date = "N/A" # Fallback if date cannot be retrieved

    return {
        "title": title,
        "source_name": source_name,
        "publish_date": publish_date,
        "url": f"file:///{filepath.replace(os.sep, '/')}" # Use file:// URI as a placeholder "URL"
    }

def load_articles_from_files(file_paths: List[str]) -> List[Dict[str, str]]:
    """
    Loads article content and simulates metadata from a list of absolute .txt file paths.
    """
    articles = []
    for full_filepath in file_paths: # Now expecting full paths directly
        print(f"--- LOADING ARTICLE: Attempting to load from file: {full_filepath} ---")
        
        content = _read_text_file(full_filepath)

        if content:
            metadata = _infer_metadata_from_filename(full_filepath)
            article_data = {
                "title": metadata["title"],
                "content": content,
                "source_name": metadata["source_name"],
                "url": metadata["url"],
                "publish_date": metadata["publish_date"]
            }
            articles.append(article_data)
        else:
            print(f"Skipping article for file {full_filepath} due to empty content or read error.")
    return articles

# Example Usage (for testing this module directly)
if __name__ == "__main__":
    import json

    # Define your absolute file paths directly here
    file1path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article1_national_voice.txt"
    file2path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article2_vigilant_daily.txt"
    # Note the 'r' before the string to treat it as a raw string,
    # preventing backslashes from being interpreted as escape sequences.

    print("--- TEST CASE 1: Loading Single Article ---")
    single_article_paths = [file1path] 
    single_article_data = load_articles_from_files(single_article_paths)
    print("\n--- Loaded Single Article Data ---")
    print(json.dumps(single_article_data, indent=2))

    print("\n--- TEST CASE 2: Loading Two Contrasting Articles ---")
    multiple_article_paths = [
        file1path, 
        file2path
    ]
    multiple_article_data = load_articles_from_files(multiple_article_paths)
    print("\n--- Loaded Multiple Article Data ---")
    print(json.dumps(multiple_article_data, indent=2))

    print("\n--- TEST CASE 3: Loading a Non-Existent Article ---")
    non_existent_article_paths = [r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\non_existent_article.txt"] # Example non-existent
    non_existent_article_data = load_articles_from_files(non_existent_article_paths)
    print("\n--- Loaded Non-Existent Article Data (should be empty) ---")
    print(json.dumps(non_existent_article_data, indent=2))