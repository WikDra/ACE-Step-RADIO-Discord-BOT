"""
Windows-specific configuration for ACE-Step Discord Bot
"""
import os
from pathlib import Path

# ==================== PATHS ====================
# Bazuj na rzeczywistych ścieżkach z ACE-Step
HOME_DIR = Path.home()
CACHE_DIR = HOME_DIR / ".cache" / "ace-step"
MODELS_DIR = CACHE_DIR / "checkpoints" 
OUTPUT_DIR = HOME_DIR / "ace_discord_output"
TEMP_DIR = HOME_DIR / "ace_temp"

# ==================== MODELS ====================
# Z radio_gradio.py
LLM_MODEL_NAME = "gemma-3-12b-it-abliterated.q4_k_m.gguf"
LLM_MODEL_PATH = MODELS_DIR / LLM_MODEL_NAME
ACE_CHECKPOINT_PATH = MODELS_DIR

# ==================== DISCORD ====================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"
MAX_GUILDS = 100
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB limit Discord dla uploadów

# ==================== AUDIO ====================  
# Discord audio settings
DISCORD_SAMPLE_RATE = 48000
DISCORD_CHANNELS = 2
DISCORD_FRAME_SIZE = 20  # ms

# ACE-Step defaults z radio_gradio.py
DEFAULT_GENRE = "pop"
DEFAULT_THEME = "love"
DEFAULT_LANGUAGE = "english"  
DEFAULT_DURATION = 60
MAX_LENGTH_MIN = 30
MAX_LENGTH_MAX = 300
BUFFER_SIZE = 3

# ==================== PERFORMANCE ====================
CPU_OFFLOAD = False  # Set True dla słabszych GPU
LLM_CONTEXT_SIZE = 4096
LLM_GPU_LAYERS = -1  # -1 = all layers on GPU
TORCH_DTYPE = "float16"  # float32 dla CPU
