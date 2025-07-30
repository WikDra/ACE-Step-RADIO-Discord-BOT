"""
Windows-specific configuration for ACE-Step Discord Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import torch for GPU detection (graceful fallback if not available)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# ==================== PATHS ====================
# Bazuj na rzeczywistych ścieżkach z ACE-Step
HOME_DIR = Path.home()
CACHE_DIR = HOME_DIR / ".cache" / "ace-step"
MODELS_DIR = CACHE_DIR / "checkpoints" 
OUTPUT_DIR = HOME_DIR / "ace_discord_output"
TEMP_DIR = HOME_DIR / "ace_temp"

# ==================== MODELS ====================
# LLM Model Configuration
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf")
LLM_MODEL_PATH = MODELS_DIR / LLM_MODEL_NAME
LLM_MODEL_URL = "https://huggingface.co/mradermacher/Huihui-gemma-3n-E4B-it-abliterated-GGUF/resolve/main/Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf"

# ACE-Step Models
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

# LLM Performance Settings
LLM_CONTEXT_SIZE = 8192  # Increased for better lyrics generation
LLM_GPU_LAYERS = int(os.getenv("LLM_GPU_LAYERS", "-1"))  # -1 = all layers on GPU, 0 = CPU only
# Smart allocation: When ACE-Step uses CPU offload, LLM can use GPU (optimal 8GB VRAM usage)
LLM_GPU_ENABLED = TORCH_AVAILABLE and torch.cuda.is_available()  # Always try GPU if available
print(f"🔍 Settings Debug - CPU_OFFLOAD: {CPU_OFFLOAD}")
print(f"🔍 Settings Debug - TORCH_AVAILABLE: {TORCH_AVAILABLE}")
print(f"🔍 Settings Debug - torch.cuda.is_available(): {torch.cuda.is_available() if TORCH_AVAILABLE else 'N/A'}")
print(f"🔍 Settings Debug - LLM_GPU_ENABLED: {LLM_GPU_ENABLED}")
print(f"🔍 Settings Debug - LLM_GPU_LAYERS: {LLM_GPU_LAYERS}")
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
DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", "60"))  # Read from .env
MAX_LENGTH_MIN = 30
MAX_LENGTH_MAX = int(os.getenv("MAX_LENGTH_MAX", "300"))  # Read from .env
BUFFER_SIZE = 2 if CPU_OFFLOAD else 3  # Smaller buffer for limited VRAM
