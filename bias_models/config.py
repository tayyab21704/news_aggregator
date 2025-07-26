# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# 🔐 API Keys
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")

# 🌐 Language Settings
TARGET_LANG = "en"
MAX_TOKENS = 500  # For chunking

# 📦 Model Names
TRANSLATOR_MODEL = "facebook/m2m100_418M"  # or try "Helsinki-NLP/opus-mt-xx-en"
SENTIMENT_MODEL = "bhadresh-savani/distilbert-base-uncased-emotion" 
BIAS_MODEL = "matous-volf/political-leaning-politics"  # Or a more robust bias-specific model
TRANSLATOR_MODEL="Helsinki-NLP/opus-mt-hi-en"
# 🧠 Task Configurations
USE_LOCAL_MODELS = True # Toggle this if switching to offline
DEVICE = "cpu"  # or 'cuda' if GPU available
