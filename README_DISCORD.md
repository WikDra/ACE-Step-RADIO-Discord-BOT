# 🎵 ACE-Step Discord Radio Bot

Bot Discord do generowania muzyki AI w czasie rzeczywistym, bazujący na **ACE-Step** i **PasiKoodaa/ACE-Step-RADIO**.

## 🚀 Szybki Start

### 1. Instalacja

```bash
# Klonuj repozytorium
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT

# Uruchom setup (Windows)
setup.bat
```

### 2. Konfiguracja

```bash
# Ustaw token Discord w pliku .env
echo DISCORD_TOKEN=twój_token_tutaj > .env

# Lub w PowerShell:
$env:DISCORD_TOKEN="twój_token_tutaj"
```

### 3. Uruchomienie

```bash
# Aktywuj środowisko
conda activate ace-radio
# lub: ace-radio-venv\Scripts\activate.bat

# Uruchom bota
python discord_bot/bot.py
```

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
| `/radio_genre` | Ustaw gatunek | pop, rock, jazz, edm, classical, hip-hop, country, blues, reggae, ambient |
| `/radio_theme` | Ustaw temat | love, party, energetic, chill, motivational, sad, romantic |
| `/radio_language` | Ustaw język | polish, english, spanish, french, german, italian, russian, chinese, japanese, korean |
| `/radio_maxlength` | Max długość | 30-300 sekund |

### Kolejka
| Komenda | Opis |
|---------|------|
| `/radio_auto` | Auto-dodawanie utworów |
| `/radio_queue_list` | Pokaż kolejkę |

### Info
| Komenda | Opis |
|---------|------|
| `/radio_settings` | Obecne ustawienia |
| `/radio_nowplaying` | Co teraz gra |
| `/radio_preset` | Gotowe kombinacje |
| `/radio_help` | Pełna lista komend |

## 🎨 Presety

| Preset | Gatunek | Temat | Język | Opis |
|--------|---------|-------|-------|------|
| `party` | EDM | energetic | english | Energetyczna muzyka do tańca |
| `chill` | Ambient | relaxing | english | Spokojna muzyka do relaksu |
| `polish_pop` | Pop | love | polish | Polski pop o miłości |
| `workout` | Electronic | motivational | english | Motywująca muzyka do ćwiczeń |
| `romantic` | Pop | love | current | Romantyczne utwory |
| `focus` | Ambient | calm | instrumental | Muzyka do koncentracji |

Użycie: `/radio_preset preset_name:party`

## ⚙️ Wymagania Systemowe

### Minimalne
- **Python:** 3.8+
- **RAM:** 8GB
- **GPU:** 4GB VRAM (CUDA) lub CPU
- **Dysk:** 10GB wolnej przestrzeni

### Zalecane  
- **Python:** 3.10+
- **RAM:** 16GB+
- **GPU:** 8GB+ VRAM (RTX 3070/4060 lub lepsze)
- **Dysk:** 20GB+ SSD

### Oprogramowanie
- **FFmpeg** (do konwersji audio)
- **CUDA Toolkit** 11.8+ (dla GPU)
- **Conda** lub **venv** (do środowiska Python)

## 📦 Zależności

Główne pakiety:
```
discord.py>=2.3.0      # Discord API
torch>=2.0.0           # PyTorch dla AI
transformers>=4.40.0   # Hugging Face transformers
llama-cpp-python       # LLM dla tekstów
librosa                # Analiza audio
soundfile              # I/O audio
gradio>=4.0.0          # UI (opcjonalne)
```

Pełna lista w `requirements_discord.txt`.

## 🔧 Konfiguracja Zaawansowana

### Zmienne Środowiskowe

```bash
# Wymagane
DISCORD_TOKEN=twój_token_bota

# Opcjonalne
CUDA_VISIBLE_DEVICES=0     # ID GPU
ACE_CHECKPOINT_PATH=./checkpoints
LLM_MODEL_PATH=./models/llama.gguf
```

### Pliki Konfiguracyjne

- `discord_bot/config/settings.py` - Główne ustawienia
- `discord_bot/config/constants.py` - Stałe i komunikaty
- `discord_bot/data/presets.json` - Presety muzyczne
- `discord_bot/data/languages.json` - Obsługiwane języki

### Optymalizacja Wydajności

#### GPU (zalecane)
```python
# discord_bot/config/settings.py
CPU_OFFLOAD = False
TORCH_DTYPE = "float16"
LLM_GPU_LAYERS = -1  # Wszystkie warstwy na GPU
```

#### CPU (słabsze karty)
```python
CPU_OFFLOAD = True
TORCH_DTYPE = "float32"
LLM_GPU_LAYERS = 0  # LLM na CPU
```

## 🎵 Jak Działa Generowanie Muzyki

1. **Teksty:** LLM (Llama) generuje teksty na podstawie gatunku/tematu
2. **Muzyka:** ACE-Step tworzy audio na podstawie tekstów i parametrów
3. **Konwersja:** FFmpeg dostosowuje audio dla Discord (PCM 48kHz)
4. **Upload:** Opcjonalna konwersja do MP3 dla udostępniania

### Proces Generowania
```
Komenda → Walidacja → Generowanie tekstów → Generowanie muzyki → Konwersja → Odtwarzanie
     ↓
Discord Response (5-30 sekund)
```

## 🛠️ Rozwiązywanie Problemów

### Bot nie odpowiada
1. Sprawdź token Discord w `.env`
2. Sprawdź uprawnienia bota na serwerze
3. Restart środowiska: `conda activate ace-radio`

### Błędy generowania
```bash
# Sprawdź CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Sprawdź modele
ls ~/.cache/ace-step/checkpoints

# Sprawdź miejsce na dysku
df -h  # Linux/Mac
dir C:\ # Windows
```

### Problemy audio
```bash
# Sprawdź FFmpeg
ffmpeg -version

# Test konwersji
ffmpeg -i input.wav -f s16le -ar 48000 -ac 2 output.pcm
```

### Błędy uploadu
- Sprawdź rozmiar pliku (max 8MB Discord)
- Sprawdź format (preferowany MP3)
- Sprawdź uprawnienia kanału

### Logi i Debugowanie
```bash
# Logi bota
tail -f discord_radio.log

# Verbose mode
python discord_bot/bot.py --debug

# Test bez Discord
python -m pytest test_radio_bot.py -v
```

## 🔄 Aktualizacja

### Aktualizacja z upstream ACE-Step:
```bash
# Fetch najnowsze zmiany
git fetch upstream
git merge upstream/main

# Rozwiąż konflikty zachowując Discord kod
git add .
git commit -m "Merge upstream changes"

# Aktualizuj zależności
pip install -r requirements_discord.txt --upgrade
```

### Backup ustawień:
```bash
# Zapisz konfigurację
cp discord_bot/config/settings.py settings_backup.py

# Po aktualizacji przywróć ustawienia
cp settings_backup.py discord_bot/config/settings.py
```

## 🤝 Rozwój

### Struktura Projektu
```
discord_bot/
├── bot.py              # Główny plik bota
├── cogs/
│   └── radio_cog.py    # Komendy Discord
├── utils/
│   ├── radio_engine.py # Adaptacja radio_gradio.py
│   ├── queue_manager.py # Zarządzanie kolejką
│   └── audio_converter.py # Konwersja audio
├── config/
│   ├── settings.py     # Ustawienia
│   └── constants.py    # Stałe
└── data/
    ├── presets.json    # Presety
    └── languages.json  # Języki
```

### Dodawanie Nowych Funkcji

1. **Nowe komendy:** Dodaj do `radio_cog.py`
2. **Nowe presety:** Edytuj `data/presets.json`
3. **Nowe języki:** Dodaj do `constants.py` i `languages.json`
4. **Konfiguracja:** Edytuj `settings.py`

### Testowanie
```bash
# Uruchom testy
python -m pytest test_radio_bot.py -v

# Test konkretnej funkcji
python -m pytest test_radio_bot.py::TestRadioQueue::test_max_length_validation -v

# Coverage
pip install pytest-cov
python -m pytest --cov=discord_bot test_radio_bot.py
```

## 📊 Monitoring i Metryki

Bot automatycznie loguje:
- Liczba wygenerowanych utworów
- Błędy generowania
- Użycie zasobów
- Aktywne serwery
- Statystyki komend

Logi w `discord_radio.log`.

## 📄 Licencja

Ten projekt dziedziczy licencję z [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step).

## 🙏 Podziękowania

- **ACE-Step Team** - Oryginalny model AI
- **PasiKoodaa** - ACE-Step-RADIO fork
- **Discord.py** - Discord API wrapper
- **Llama.cpp** - LLM inference

---

**Uwaga:** Bot wymaga znacznych zasobów obliczeniowych. Zalecane uruchomienie na serwerze z dedykowaną kartą graficzną.
