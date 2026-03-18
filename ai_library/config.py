# ai_library/config.py
import os


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
    TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    