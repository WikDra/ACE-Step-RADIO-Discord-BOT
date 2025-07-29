# 🎵 Instrukcja GitHub Copilot: Bot Discord z ACE-Step Radio

## 📋 Przegląd Projektu

Stworzenie bota Discord który integruje **ACE-Step Radio** (fork z PasiKoodaa/ACE-Step-RADIO) z najnowszym kodem z **ace-step/ACE-Step main branch**. Bot będzie generować muzykę w czasie rzeczywistym z komendami do kontroli gatunku, tematu, języka i długości utworów.

### 🎯 Główne Cele
- Aktualizacja forka do najnowszego upstream
- Adaptacja `radio_gradio.py` na bota Discord
- Środowisko Windows + Conda (bez Docker)
- Rozbudowane komendy slash z kontrolą parametrów
- Komenda do ustawiania maksymalnej długości utworów
- System pomocy i obsługa wielu języków
- Nowa komenda do wrzucania pliku z piosenką na kanał Discord

## 🔍 Analiza Kodu Źródłowego

### 📁 Struktura ACE-Step-RADIO (obecna)
```
ACE-Step-RADIO/
├── radio_gradio.py          # 🔑 GŁÓWNY PLIK - cała logika Radio
├── acestep/                 # Moduł z oryginalnego repo
│   ├── __init__.py
│   ├── cli.py              # acestep --port 7865
│   ├── models/             # Modele AI (DiffusionTransformer)
│   ├── schedulers/         # Flow matching schedulers
│   ├── inference/          # generate_audio, sampling
│   └── utils/              # Utility functions
├── requirements.txt        # Zależności projektu
├── checkpoints/           # Auto-downloaded models
└── README.md
```

### 🧩 Kluczowe Komponenty z `radio_gradio.py`
```python
# RZECZYWISTE IMPORTY do wykorzystania:
import gradio as gr
from llama_cpp import Llama
import torch
from acestep.models import load_model
from acestep.inference import generate_audio
from acestep import ACEStepPipeline
from acestep.schedulers import FlowMatchEulerDiscreteScheduler
```

### 🎛️ Główne Funkcje do Adaptacji
1. **`generate_lyrics_with_llm()`** - LLM generuje teksty
2. **`generate_music_with_ace()`** - ACE-Step tworzy audio
3. **`buffer_management()`** - kolejka utworów
4. **`audio_streaming()`** - strumieniowanie audio

## ⚙️ Setup Środowiska Windows + Conda

### 🔧 Instalacja (plik `setup.bat`)
```batch
@echo off
echo 🎵 ACE-Step Discord Radio Setup
echo.

REM 1. Klonowanie własnego forka
echo [1/6] Klonowanie repozytorium...
git clone https://github.com/[TWOJA-NAZWA]/ACE-Step-RADIO.git
cd ACE-Step-RADIO

REM 2. Dodanie upstream dla aktualizacji
echo [2/6] Dodawanie upstream...
git remote add upstream https://github.com/ace-step/ACE-Step.git
git fetch upstream

REM 3. Merge z najnowszym main
echo [3/6] Aktualizacja do najnowszego ACE-Step...
git checkout -b discord-update
git merge upstream/main
echo ⚠️  Rozwiąż konflikty ręcznie zachowując radio_gradio.py

REM 4. Tworzenie środowiska Conda
echo [4/6] Tworzenie środowiska Conda...
conda create -n ace-radio python=3.10 -y
call conda activate ace-radio

REM 5. Instalowanie zależności
echo [5/6] Instalowanie zależności...
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install discord.py>=2.3.0 gradio>=4.0.0 llama-cpp-python triton-windows
pip install transformers>=4.40.0 accelerate soundfile librosa
pip install -e .

REM 6. Konfiguracja
echo [6/6] Konfiguracja...
echo set DISCORD_TOKEN=TWOJ_TOKEN_TUTAJ > .env
echo.
echo ✅ Setup zakończony! Ustaw DISCORD_TOKEN i uruchom:
echo python discord_bot/bot.py
pause
```

### 📦 `requirements_discord.txt`
```txt
# Core Discord
discord.py>=2.3.0

# Audio & AI
torch>=2.0.0
torchaudio
transformers>=4.40.0
accelerate
llama-cpp-python
soundfile
librosa

# UI (opcjonalne - zachowanie Gradio)
gradio>=4.0.0

# Windows specific
triton-windows

# Development
pytest
black
ruff
```

## 🏗️ Struktura Projektu Discord

```
discord_bot/
├── bot.py                    # 🤖 Główny plik bota
├── cogs/
│   └── radio_cog.py         # 🎵 Komendy Radio
├── utils/
│   ├── radio_engine.py      # 🔧 Adaptacja radio_gradio.py
│   ├── queue_manager.py     # 📋 Zarządzanie kolejką
│   └── audio_converter.py   # 🎧 Konwersja do Discord
├── config/
│   ├── settings.py          # ⚙️ Ustawienia Windows
│   └── constants.py         # 📊 Stałe i enums
└── data/
    ├── presets.json         # 🎨 Gotowe presety
    └── languages.json       # 🌍 Obsługiwane języki
```

## 🎵 RadioEngine - Adaptacja radio_gradio.py

### 📝 Copilot Instrukcja: `utils/radio_engine.py`

```python
"""
COPILOT: Stwórz klasę RadioEngine bazując DOKŁADNIE na radio_gradio.py

KLUCZOWE KOMPONENTY do przeniesienia:
1. Inicjalizacja LLM i ACE-Step (linie 15-45 w radio_gradio.py)
2. Funkcje generowania (linie 60-120)
3. Buffer management (linie 130-180)
4. Error handling (linie 200-250)
"""

import asyncio
import torch
from pathlib import Path
from llama_cpp import Llama
from acestep import ACEStepPipeline
from acestep.schedulers import FlowMatchEulerDiscreteScheduler

class RadioEngine:
    def __init__(self, checkpoint_path: str = None, cpu_offload: bool = False):
        """
        COPILOT: Inicjalizacja bazująca na radio_gradio.py linie 15-45:
        
        1. Załaduj LLM Llama:
           - model_path = "gemma-3-12b-it-abliterated.q4_k_m.gguf"
           - n_ctx = 4096
           - n_gpu_layers = -1 if not cpu_offload else 0
           - verbose = False
        
        2. Załaduj ACE-Step Pipeline:
           - checkpoint_path = checkpoint_path or "~/.cache/ace-step"
           - device = "cuda" if torch.cuda.is_available() and not cpu_offload else "cpu"
           - torch_dtype = torch.float16 if device == "cuda" else torch.float32
        
        3. Załaduj Scheduler:
           - FlowMatchEulerDiscreteScheduler.from_pretrained(checkpoint_path)
        
        4. Setup paths:
           - self.output_dir = Path("discord_output")
           - self.cache_dir = Path("discord_cache")
           - self.temp_dir = Path("temp_audio")
        """
        
    async def generate_lyrics_async(self, genre: str, theme: str, language: str) -> str:
        """
        COPILOT: Adaptuj generate_lyrics_with_llm() z radio_gradio.py (linie 60-85):
        
        1. Stwórz prompt w formacie:
           f"Create a {genre} song in {language} about {theme}. 
           Write only lyrics, no descriptions. 
           Structure: verse, chorus, verse, chorus, bridge, chorus."
        
        2. Wywołaj LLM w executor:
           loop = asyncio.get_event_loop()
           return await loop.run_in_executor(None, self._generate_lyrics_sync, prompt)
        
        3. _generate_lyrics_sync():
           - self.llm(prompt, max_tokens=512, temperature=0.7)
           - Extract text from response
           - Clean formatting
        """
    
    async def generate_music_async(self, lyrics: str, tags: str, duration: int, max_length: int) -> Path:
        """
        COPILOT: Adaptuj generate_music_with_ace() z radio_gradio.py (linie 90-120):
        
        1. Waliduj duration vs max_length:
           actual_duration = min(duration, max_length)
        
        2. Przygotuj inputs:
           - text_input = lyrics
           - music_tags = tags
           - audio_duration = actual_duration
        
        3. Generate w executor:
           loop = asyncio.get_event_loop()
           audio_data = await loop.run_in_executor(
               None, self._generate_music_sync, lyrics, tags, actual_duration
           )
        
        4. _generate_music_sync():
           - self.pipeline(prompt=lyrics, tags=tags, duration=actual_duration)
           - Save to temp file
           - Return Path object
        """
    
    def convert_for_discord(self, audio_path: Path) -> Path:
        """
        COPILOT: Konwertuj audio dla Discord:
        
        1. Użyj FFmpeg przez subprocess:
           - Input: audio_path (WAV/OGG z ACE-Step)
           - Output: PCM 48kHz stereo dla Discord
           - Command: ffmpeg -i input.wav -f s16le -ar 48000 -ac 2 output.pcm
        
        2. Error handling:
           - Check if FFmpeg installed
           - Validate input file
           - Clean temp files
        """
    
    def prepare_upload_file(self, audio_path: Path, format: str = "wav") -> Path:
        """
        COPILOT: NOWA FUNKCJA - Przygotuj plik do uploadu na Discord:
        
        1. Sprawdź czy plik istnieje w audio_path
        2. Skopiuj lub konwertuj do żądanego formatu (np. WAV, MP3)
        3. Command: ffmpeg -i input.pcm -c:a libmp3lame output.mp3 (jeśli konwersja potrzebna)
        4. Return Path do gotowego pliku
        5. Dodaj metadane jeśli możliwe (nazwa pliku z genre-theme-duration)
        """
```

## 📋 QueueManager - Zarządzanie Kolejką

### 📝 Copilot Instrukcja: `utils/queue_manager.py`

```python
"""
COPILOT: Stwórz system kolejki bazując na buffer logic z radio_gradio.py
"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import json

@dataclass
class TrackInfo:
    """
    COPILOT: Struktura informacji o utworze:
    - path: Path - ścieżka do pliku audio
    - genre: str - gatunek
    - theme: str - temat  
    - language: str - język
    - duration: int - długość w sekundach
    - lyrics: str - tekst utworu
    - generated_at: datetime - kiedy wygenerowano
    """

class RadioQueue:
    def __init__(self):
        """
        COPILOT: Inicjalizacja kolejki z domyślnymi ustawieniami:
        
        USTAWIENIA DOMYŚLNE (z radio_gradio.py):
        - current_genre = "pop"
        - current_theme = "love"
        - current_language = "english"  
        - max_length = 60  # NOWA FUNKCJA
        - buffer_size = 3
        - auto_queue = True
        
        STRUKTURY DANYCH:
        - queue: List[TrackInfo] = []
        - history: List[TrackInfo] = []
        - current_track: Optional[TrackInfo] = None
        
        OBSŁUGIWANE JĘZYKI (z ACE-Step docs):
        - SUPPORTED_LANGUAGES = ["english", "chinese", "russian", "spanish", 
          "japanese", "german", "french", "portuguese", "italian", "korean", "polish"]
        """
    
    def set_max_length(self, seconds: int) -> bool:
        """
        COPILOT: NOWA KOMENDA - walidacja i ustawienie max długości:
        
        1. Waliduj zakres: 30  bool:
        """
        COPILOT: Walidacja i ustawienie języka:
        
        1. Sprawdź czy language.lower() in SUPPORTED_LANGUAGES
        2. Jeśli OK: self.current_language = language.lower(), return True  
        3. Jeśli błąd: return False
        """
    
    async def ensure_buffer_full(self, radio_engine) -> None:
        """
        COPILOT: Auto-filling buffer jak w radio_gradio.py:
        
        1. Sprawdź czy len(self.queue)  dict:
        """
        COPILOT: Return current settings jako dict:
        {
            "genre": self.current_genre,
            "theme": self.current_theme, 
            "language": self.current_language,
            "max_length": self.max_length,
            "auto_queue": self.auto_queue,
            "queue_length": len(self.queue)
        }
        """
    
    def get_track_path(self, track_index: Optional[int] = None) -> Optional[Path]:
        """
        COPILOT: NOWA FUNKCJA - Pobierz ścieżkę pliku z kolejki:
        
        1. Jeśli track_index None: return current_track.path
        2. Jeśli podany: return queue[track_index].path
        3. Jeśli poza zakresem: return None
        """
```

## 🤖 Radio Cog - Komendy Discord

### 📝 Copilot Instrukcja: `cogs/radio_cog.py`

```python
"""
COPILOT: Główny cog z komendami Discord
Używa RadioEngine i RadioQueue do implementacji wszystkich funkcji
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

class RadioCog(commands.Cog):
    def __init__(self, bot):
        """
        COPILOT: Inicjalizacja cog:
        
        - self.bot = bot
        - self.radio_engine = RadioEngine()
        - self.voice_clients = {}  # guild_id: discord.VoiceClient
        - self.queues = {}        # guild_id: RadioQueue  
        - self.playing_tasks = {} # guild_id: asyncio.Task
        """

    # ==================== PODSTAWOWE KOMENDY ====================
    
    @commands.slash_command(description="Dołącz do kanału głosowego")
    async def radio_join(self, ctx):
        """
        COPILOT: Standard Discord voice join:
        
        1. Sprawdź czy user jest w voice channel
        2. Jeśli bot już połączony - przenieś
        3. Jeśli nie - połącz do user voice channel  
        4. Zapisz voice_client w self.voice_clients[ctx.guild.id]
        5. Embed potwierdzenia: "🎵 Dołączyłem do {channel.name}"
        """
    
    @commands.slash_command(description="Zagraj utwór z podanymi parametrami")
    async def radio_play(self, ctx,
                        genre: str = "pop",
                        theme: str = "love", 
                        language: str = "english",
                        duration: int = 60):
        """
        COPILOT: Główna komenda odtwarzania:
        
        1. Sprawdź czy bot w voice channel
        2. Get/create RadioQueue dla guild
        3. Update queue settings jeśli podane
        4. Wywołaj radio_engine.generate_lyrics_async()
        5. Wywołaj radio_engine.generate_music_async() 
        6. Convert dla Discord przez radio_engine.convert_for_discord()
        7. Play przez voice_client.play(discord.FFmpegPCMAudio(source))
        8. Embed z info o utworze (genre, theme, language, duration)
        9. Start auto-queue task jeśli włączone
        """
    
    @commands.slash_command(description="Pomiń obecny utwór")
    async def radio_skip(self, ctx):
        """
        COPILOT: Skip current track:
        
        1. Stop current playback: voice_client.stop()
        2. Get next from queue lub emergency generate
        3. Play next track  
        4. Embed: "⏭️ Pominięto utwór"
        """
    
    @commands.slash_command(description="Zatrzymaj radio i opuść kanał")
    async def radio_stop(self, ctx):
        """
        COPILOT: Stop and cleanup:
        
        1. Stop playback
        2. Disconnect voice_client
        3. Cancel auto-queue task  
        4. Clear queue i cache
        5. Embed: "⏹️ Radio zatrzymane"
        """
    
    @commands.slash_command(description="Wrzuć plik z obecnym utworem na kanał")
    async def radio_upload(self, ctx, track_index: Optional[int] = None):
        """
        COPILOT: NOWA KOMENDA - Wrzuć plik z piosenką na kanał:
        
        1. Get RadioQueue dla guild
        2. Pobierz ścieżkę pliku: queue.get_track_path(track_index)
        3. Jeśli None: embed "❌ Brak utworu do uploadu"
        4. Przygotuj plik: radio_engine.prepare_upload_file(audio_path, format="mp3")
        5. Upload: await ctx.send(file=discord.File(upload_path))
        6. Embed: "📤 Plik z utworem wrzucony! (genre: {genre}, theme: {theme})"
        7. Opcjonalnie: usuń plik po uploadzie jeśli niepotrzebny
        8. Walidacja: Sprawdź czy plik  - pop, rock, jazz, edm, classical, hip-hop
        /radio_theme  - love, party, sad, energetic, chill, motivational
        /radio_language  - polish, english, spanish, french, german, italian
        /radio_maxlength  - Maksymalna długość utworów
        
        KOLEJKA:
        /radio_auto  - Auto-dodawanie utworów
        /radio_queue_add [genre] [theme] [count] - Dodaj do kolejki
        /radio_queue_list - Pokaż kolejkę
        
        INFO:
        /radio_settings - Obecne ustawienia
        /radio_nowplaying - Co gra
        /radio_preset  - Gotowe kombinacje
        
        💡 Wszystkie parametry są opcjonalne!
        """

    # ==================== PRESETY ====================
    
    @commands.slash_command(description="Użyj gotowego presetu")
    async def radio_preset(self, ctx, preset_name: str):
        """
        COPILOT: Predefiniowane kombinacje:
        
        PRESETY:
        - "party" -> genre=edm, theme=energetic, language=english
        - "chill" -> genre=ambient, theme=relaxing, language=english  
        - "polish_pop" -> genre=pop, theme=love, language=polish
        - "workout" -> genre=electronic, theme=motivational, language=english
        - "romantic" -> genre=pop, theme=love, language=current
        - "focus" -> genre=ambient, theme=calm, language=instrumental
        
        1. Load preset from presets.json or hardcoded dict
        2. Update queue settings
        3. Optionally start playing immediately
        """
```

## ⚙️ Konfiguracja i Ustawienia

### 📝 `config/settings.py`
```python
"""
COPILOT: Windows-specific configuration
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
```

### 📝 `config/constants.py`  
```python
"""
COPILOT: Stałe i enums
"""
from enum import Enum

class SupportedLanguages(Enum):
    """Z ACE-Step documentation"""
    ENGLISH = ("english", "🇺🇸")
    POLISH = ("polish", "🇵🇱") 
    SPANISH = ("spanish", "🇪🇸")
    FRENCH = ("french", "🇫🇷")
    GERMAN = ("german", "🇩🇪")
    ITALIAN = ("italian", "🇮🇹")
    PORTUGUESE = ("portuguese", "🇵🇹")
    RUSSIAN = ("russian", "🇷🇺")
    CHINESE = ("chinese", "🇨🇳")
    JAPANESE = ("japanese", "🇯🇵")
    KOREAN = ("korean", "🇰🇷")

class MusicGenres(Enum):
    """Sugerowane gatunki dla ACE-Step"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    EDM = "edm"
    HIP_HOP = "hip-hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    AMBIENT = "ambient"

class MusicThemes(Enum):
    """Sugerowane tematy"""
    LOVE = "love"
    PARTY = "party"
    SAD = "sad"
    ENERGETIC = "energetic"
    CHILL = "chill"
    MOTIVATIONAL = "motivational"
    ROMANTIC = "romantic"
    NOSTALGIC = "nostalgic"
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"

# Error messages
ERROR_MESSAGES = {
    "not_in_voice": "❌ Musisz być w kanale głosowym!",
    "bot_not_connected": "❌ Bot nie jest połączony z kanałem głosowym!",
    "invalid_language": "❌ Nieobsługiwany język. Dostępne: {languages}",
    "invalid_duration": "❌ Długość musi być między {min} a {max} sekund.",
    "generation_failed": "❌ Błąd generowania utworu. Spróbuj ponownie.",
    "no_permission": "❌ Brak uprawnień do dołączenia do kanału głosowego!",
    "file_too_large": "❌ Plik jest za duży do uploadu (max 8MB)!",
    "no_track": "❌ Brak utworu do uploadu!",
}

# Success messages
SUCCESS_MESSAGES = {
    "joined": "🎵 Dołączyłem do **{channel}**!",
    "playing": "▶️ Teraz gra: **{title}**",
    "skipped": "⏭️ Utwór pominięty",
    "stopped": "⏹️ Radio zatrzymane",
    "setting_updated": "✅ {setting} zmienione na **{value}**",
    "uploaded": "📤 Plik z utworem wrzucony! (format: MP3)",
}
```

## 🚀 Główny Plik Bota

### 📝 `bot.py`
```python
"""
COPILOT: Main Discord bot file
"""

import discord
from discord.ext import commands
import asyncio
import logging
from pathlib import Path

# Local imports
from config.settings import *
from cogs.radio_cog import RadioCog
from utils.radio_engine import RadioEngine

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_radio.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== BOT SETUP ====================
class RadioBot(commands.Bot):
    def __init__(self):
        """
        COPILOT: Inicjalizacja bota:
        
        1. Intents setup:
           - intents = discord.Intents.default()
           - intents.voice_states = True
           - intents.message_content = True
        
        2. Bot init:
           - super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        
        3. Setup paths:
           - Utwórz katalogi: OUTPUT_DIR, TEMP_DIR, CACHE_DIR
        """
        
    async def setup_hook(self):
        """
        COPILOT: Setup hook - ładowanie cogs:
        
        1. Załaduj RadioCog: await self.add_cog(RadioCog(self))
        2. Sync slash commands: await self.tree.sync()
        3. Logger info o załadowanych komendach
        """
        
    async def on_ready(self):
        """
        COPILOT: Bot ready event:
        
        1. Logger info: f"Bot zalogowany jako {self.user}"
        2. Status activity: discord.Activity(type=discord.ActivityType.listening, name="/radio_help")
        3. Sprawdź dostępność modeli
        4. Wydrukuj info o guilds i komendach
        """
        
    async def on_command_error(self, ctx, error):
        """
        COPILOT: Global error handler:
        
        1. Log error details
        2. Send user-friendly error message
        3. Handle specific errors: CommandNotFound, MissingPermissions, etc.
        """

# ==================== STARTUP ====================
async def main():
    """
    COPILOT: Main startup function:
    
    1. Sprawdź DISCORD_TOKEN
    2. Pre-load RadioEngine (test model loading)
    3. Create bot instance  
    4. Start bot z error handling
    """
    
if __name__ == "__main__":
    """
    COPILOT: Entry point:
    
    1. Check dependencies (FFmpeg, CUDA)
    2. Setup signal handlers dla graceful shutdown
    3. Run main() z asyncio.run()
    """
```

## 🧪 Testy i Debugowanie

### 📝 `test_radio_bot.py`
```python
"""
COPILOT: Basic tests dla RadioBot
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

class TestRadioEngine:
    """
    COPILOT: Test RadioEngine functions:
    
    - test_llm_loading()
    - test_ace_loading() 
    - test_lyrics_generation()
    - test_music_generation()
    - test_audio_conversion()
    - test_prepare_upload_file()  # NOWY TEST
    """

class TestRadioQueue:
    """
    COPILOT: Test queue management:
    
    - test_max_length_validation()
    - test_language_validation()
    - test_auto_queue()
    - test_buffer_management()
    - test_get_track_path()  # NOWY TEST
    """

class TestDiscordCommands:
    """
    COPILOT: Test Discord commands:
    
    - test_radio_join()
    - test_radio_play()
    - test_radio_maxlength()
    - test_radio_settings()
    - test_radio_upload()  # NOWY TEST
    """
```

## 📚 Dokumentacja Użytkownika

### 📝 `README_DISCORD.md`
```markdown
# 🎵 ACE-Step Discord Radio Bot

## 🚀 Szybki Start

### 1. Instalacja
```
git clone https://github.com/[USER]/ACE-Step-RADIO.git
cd ACE-Step-RADIO
./setup.bat
```

### 2. Konfiguracja
```
# Ustaw token Discord
set DISCORD_TOKEN=twój_token_tutaj

# Uruchom bota
conda activate ace-radio
python discord_bot/bot.py
```

### 3. Podstawowe Komendy
- `/radio_join` - Dołącz do kanału
- `/radio_play` - Zagraj muzykę
- `/radio_help` - Pełna lista komend

## 📋 Wszystkie Komendy

### Podstawowe
| Komenda | Opis | Przykład |
|---------|------|----------|
| `/radio_join` | Dołącz do voice channel | `/radio_join` |
| `/radio_play` | Zagraj utwór | `/radio_play genre:rock theme:energy` |
| `/radio_skip` | Pomiń utwór | `/radio_skip` |
| `/radio_stop` | Zatrzymaj radio | `/radio_stop` |
| `/radio_upload` | Wrzuć plik z utworem na kanał | `/radio_upload track_index:0` |

### Ustawienia  
| Komenda | Opis | Zakres |
|---------|------|---------|
| `/radio_genre` | Ustaw gatunek | pop, rock, jazz, edm, classical |
| `/radio_theme` | Ustaw temat | love, party, energetic, chill |
| `/radio_language` | Ustaw język | polish, english, spanish, french |
| `/radio_maxlength` | Max długość | 30-300 sekund |

### Kolejka
| Komenda | Opis |
|---------|------|
| `/radio_auto` | Auto-dodawanie utworów |
| `/radio_queue_add` | Dodaj utwory do kolejki |
| `/radio_queue_list` | Pokaż kolejkę |

### Info
| Komenda | Opis |
|---------|------|
| `/radio_settings` | Obecne ustawienia |
| `/radio_nowplaying` | Co teraz gra |
| `/radio_preset` | Gotowe kombinacje |

## 🎨 Presety

- `party` - EDM, energetic, english
- `chill` - Ambient, relaxing
- `polish_pop` - Pop, love, polish
- `workout` - Electronic, motivational
- `romantic` - Pop, love
- `focus` - Ambient, calm

## ⚙️ Rozwiązywanie Problemów

### Bot nie odpowiada
1. Sprawdź token Discord
2. Sprawdź uprawnienia bota
3. Restart conda environment

### Błędy generowania
1. Sprawdź CUDA/GPU
2. Sprawdź miejsce na dysku
3. Restart bota

### Problemy audio/upload
1. Sprawdź FFmpeg installation
2. Sprawdź kodeki audio
3. Test z `/radio_play duration:30` i `/radio_upload`
```

## 🔄 Proces Aktualizacji

### 📝 `update_upstream.bat`
```batch
@echo off
echo 🔄 Aktualizacja do najnowszego ACE-Step

echo [1/4] Fetch upstream...
git fetch upstream

echo [2/4] Stash local changes...
git stash push -m "Discord bot changes"

echo [3/4] Merge upstream/main...
git merge upstream/main

echo [4/4] Apply stashed changes...
git stash pop

echo ✅ Aktualizacja zakończona!
echo ⚠️  Sprawdź konflikty i przetestuj bota
pause
```

## 📊 Monitoring i Metryki

### 📝 `utils/metrics.py`
```python
"""
COPILOT: Metrics i monitoring dla bota:

- Liczba wygenerowanych utworów
- Najczęściej używane gatunki/tematy  
- Błędy generowania
- Użycie zasobów (CPU/GPU/RAM)
- Aktywne serwery
- Liczba uploadów plików
"""
```

Ta szczegółowa instrukcja dla GitHub Copilot zawiera wszystkie niezbędne informacje do stworzenia w pełni funkcjonalnego bota Discord z ACE-Step Radio, uwzględniając rzeczywistą strukturę kodu, nowe funkcje jak maksymalna długość utworów, kompletny system pomocy, obsługę wielu języków oraz komendę do wrzucania pliku z piosenką na kanał.