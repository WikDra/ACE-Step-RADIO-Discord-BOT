"""
Windows-specific configuration for ACE-Step Discord Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# ==================== PERFORMANCE ====================
CPU_OFFLOAD = os.getenv("CPU_OFFLOAD", "false").lower() == "true"  # Read from .env
LLM_CONTEXT_SIZE = 4096
LLM_GPU_LAYERS = -1  # -1 = all layers on GPU
TORCH_DTYPE = "float16"  # float32 dla CPU

# ACE-Step Official Performance Settings (2025.05.10 Memory Optimization)
# Recommended for 8GB VRAM: --torch_compile true --cpu_offload true --overlapped_decode true
# NOTE: torch_compile may have issues on Windows - we'll handle fallback in code
TORCH_COMPILE = os.getenv("TORCH_COMPILE", "false").lower() == "true"  # Disabled by default on Windows
OVERLAPPED_DECODE = os.getenv("OVERLAPPED_DECODE", "true" if CPU_OFFLOAD else "false").lower() == "true"
TORCH_COMPILE_FALLBACK = True  # Auto-fallback to eager mode on torch_compile errors

# ACE-Step defaults z radio_gradio.py (after CPU_OFFLOAD is defined)
DEFAULT_GENRE = "pop"
DEFAULT_THEME = "love"
DEFAULT_LANGUAGE = "english"  
DEFAULT_DURATION = 30 if CPU_OFFLOAD else 60  # Shorter for limited VRAM
MAX_LENGTH_MIN = 30
MAX_LENGTH_MAX = 120 if CPU_OFFLOAD else 300  # Reduced max for 8GB VRAM
BUFFER_SIZE = 2 if CPU_OFFLOAD else 3  # Smaller buffer for limited VRAM
