# ai_library/config.py
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "WRONG_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
    TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
