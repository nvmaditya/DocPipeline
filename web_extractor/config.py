"""Configuration settings for the DDG pipeline."""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Settings (optional)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
USE_LLM_REWRITER = os.getenv("USE_LLM_REWRITER", "false").lower() == "true"
USE_LLM_STRUCTURER = os.getenv("USE_LLM_STRUCTURER", "false").lower() == "true"

# Search Settings
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# Cache Settings
CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

# Logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
