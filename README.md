# 🎵 ACE-Step RADIO Discord BOT

Discord bot for real-time AI music generation, based on **ACE-Step** and **PasiKoodaa/ACE-Step-RADIO**.

> **🚨 IMPORTANT**: This project combines ACE-Step AI music generation with Discord integration. It requires significant computational resources (recommended: 8GB+ VRAM GPU).

## ⚡ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+)
- **Python**: 3.10+
- **RAM**: 16GB system memory
- **GPU**: 8GB VRAM (RTX 4060/RTX 3060 8GB or better)
- **CUDA**: 11.8+ (12.4+ recommended)
- **Storage**: 20GB free space

### GPU Compatibility & VRAM Modes

Bot automatically adapts to available VRAM:

| GPU Series | Recommended CUDA | VRAM Mode | Performance |
|------------|------------------|-----------|-------------|
| **GTX 10xx, RTX 20xx** | CUDA 11.8 | CPU Offload (4-6GB) | ⚠️ Slower but functional |
| **RTX 30xx, RTX 40xx** | CUDA 12.4+ | Optimized (8GB+) | 🚀 Fast |
| **High VRAM (12GB+)** | CUDA 12.4+ | Full CUDA | 🔥 Maximum speed |

💡 **For RTX 4060 Laptop 8GB**: Set `CPU_OFFLOAD=true` in `.env`

## 🎯 Features

- **🎵 Real-time Music Generation**: Generate unique songs instantly with AI
- **🎛️ Discord Slash Commands**: Full integration with Discord's modern command system  
- **⏸️ Smart Pause/Resume**: Control playback with `/radio_pause` & `/radio_resume` - generation continues in background!
- **🌍 Multi-language Support**: Generate lyrics in 11+ languages
- **📤 File Upload**: Share generated songs as files on Discord
- **🎨 Music Presets**: Quick access to popular music combinations
- **📊 Bot Statistics**: Track usage and performance metrics
- **⚙️ Queue Management**: Auto-buffering and queue control
- **🎚️ Advanced Controls**: Genre, theme, language, and duration controls

## 🚀 Quick Start

### 1. Installation

**Windows:**
```bash
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT
setup.bat  # Run as Administrator (requires Conda)
```

**Linux:**
```bash
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT
chmod +x setup.sh
./setup.sh  # Requires Conda/Miniconda
```

> **⚠️ IMPORTANT**: Setup scripts require **Conda** for proper PyTorch/CUDA installation. Pure pip installation can cause dependency conflicts.

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your Discord bot token
DISCORD_TOKEN=your_bot_token_here
```

### 3. Run the Bot
```bash
# Activate environment
conda activate ace-radio

# Start the bot
python discord_bot/bot.py
```

## 📋 Discord Commands

| Category | Command | Description |
|----------|---------|-------------|
| **Basic** | `/radio_join` | Join voice channel |
| | `/radio_play` | Play generated music |
| | `/radio_skip` | Skip current track |
| | `/radio_pause` | Pause playback ⏸️ |
| | `/radio_resume` | Resume playback ▶️ |
| | `/radio_stop` | Stop radio & leave |
| | `/radio_upload` | Upload song file to channel |
| **Settings** | `/radio_genre` | Set music genre |
| | `/radio_theme` | Set song theme |
| | `/radio_language` | Set lyrics language |
| | `/radio_maxlength` | Set max song length |
| **Queue** | `/radio_auto` | Toggle auto-queue |
| | `/radio_queue_list` | Show queue |
| **Info** | `/radio_settings` | Show current settings |
| | `/radio_nowplaying` | Show current track |
| | `/radio_stats` | Show bot statistics |
| | `/radio_preset` | Use music presets |
| | `/radio_help` | Show all commands |

> **💡 Smart Pause/Resume**: Pause stops playback but generation continues in background to fill the buffer! Perfect for bathroom breaks while keeping music ready.

## 🎨 Music Presets

Quick-start combinations for instant music:

### Original Presets
- **`party`**: EDM + energetic + english
- **`chill`**: Ambient + relaxing + english  
- **`polish_pop`**: Pop + love + polish
- **`workout`**: Electronic + motivational + english
- **`romantic`**: Pop + love + current language
- **`focus`**: Ambient + calm + instrumental

### New in Beta
- **`lofi`**: Lo-fi beats for studying
- **`metal`**: Heavy metal music
- **`classical`**: Classical orchestral
- **`jazz`**: Smooth jazz
- **`rock`**: Classic rock
- **`sad`**: Melancholic music

## 🎵 Supported Genres & Languages

**Genres**: pop, rock, jazz, edm, classical, hip-hop, country, blues, reggae, ambient, metal, funk, disco, punk

**Languages**: English, Polish, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean

## ⚙️ Software Dependencies

- **FFmpeg**: Required for audio conversion
- **CUDA Toolkit**: 11.8+ (for GPU acceleration)
- **Conda**: For Python environment management

## 📦 Advanced Installation

### Manual Setup (All Platforms)
```bash
# 1. Create environment
conda create -n ace-radio python=3.10 -y
conda activate ace-radio

# 2. Install PyTorch with CUDA
# For RTX 30xx/40xx (CUDA 12.4+)
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
# For GTX 10xx/RTX 20xx (CUDA 11.8)
# conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 3. Install Discord bot dependencies
pip install -r requirements_discord.txt

# 4. Install ACE-Step
pip install -e .

# 5. Configure environment
cp .env.example .env
# Edit .env with your Discord token
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
DISCORD_TOKEN=your_discord_bot_token

# Optional
ACE_CHECKPOINT_PATH=./checkpoints
LLM_MODEL_PATH=./models/llama.gguf
CUDA_VISIBLE_DEVICES=0
CPU_OFFLOAD=false
```

### Performance Tuning

#### For High-End GPUs (8GB+ VRAM)
```python
# discord_bot/config/settings.py
CPU_OFFLOAD = False
TORCH_DTYPE = "float16"
LLM_GPU_LAYERS = -1
```

#### For Lower-End Hardware
```python
CPU_OFFLOAD = True
TORCH_DTYPE = "float32"  
LLM_GPU_LAYERS = 0
```

## 🎵 How Music Generation Works

1. **Command Input**: User requests music via Discord slash command
2. **Lyric Generation**: LLM (Llama) creates lyrics based on genre/theme/language
3. **Music Generation**: ACE-Step AI generates audio from lyrics and musical parameters
4. **Audio Processing**: FFmpeg converts audio for Discord playback (PCM 48kHz)
5. **Playback**: Bot streams audio to Discord voice channel
6. **File Sharing**: Optional conversion to MP3 for file uploads

### Generation Pipeline
```
Discord Command → Validation → Lyric Gen → Music Gen → Audio Convert → Playback
                                ↓
                        Response (5-30 seconds)
```

## 🛠️ Troubleshooting

### Bot Won't Start
```bash
# Check Discord token
echo $DISCORD_TOKEN

# Check Python environment
conda list | grep discord

# Check model files
ls ~/.cache/ace-step/checkpoints/
```

### Generation Errors
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check disk space
df -h  # Linux/macOS
dir C:\ # Windows

# Check FFmpeg
ffmpeg -version
```

### Audio Issues
```bash
# Test audio conversion
ffmpeg -i input.wav -f s16le -ar 48000 -ac 2 output.pcm

# Check file permissions
ls -la discord_output/
```

### Memory Issues

**High VRAM usage (>8GB)?**
1. Check CUDA version: `nvidia-smi`
2. Update CUDA to 12.4+ for better optimization
3. Set `CPU_OFFLOAD=true` in `.env`
4. Run setup script as Administrator (Windows) or with sudo (Linux)
5. Restart conda environment

**Quick Fixes:**
- Enable `CPU_OFFLOAD = True` in settings
- Set `TORCH_COMPILE = False` if unstable
- Clear model cache: `~/.cache/huggingface`
- Reduce `MAX_LENGTH_MAX` in settings
- Restart bot periodically

## 📊 Bot Statistics

The bot automatically tracks:
- Total songs generated
- Average generation time
- Popular genres and languages
- Command usage statistics
- Memory and performance metrics
- Active servers and voice connections

View with `/radio_stats` command.

## 🔄 Updates & Maintenance

### Update from ACE-Step upstream:
```bash
./update_upstream.bat  # Windows
# or manually:
git fetch upstream
git merge upstream/main
pip install -r requirements_discord.txt --upgrade
```

### Backup Settings:
```bash
cp discord_bot/config/settings.py settings_backup.py
```

## 🏗️ Development & Contributing

### Project Structure
```
discord_bot/
├── bot.py                 # Main bot file
├── cogs/
│   └── radio_cog.py      # Discord commands
├── utils/
│   ├── radio_engine.py   # Music generation engine
│   ├── queue_manager.py  # Queue management
│   ├── audio_converter.py # Audio processing
│   └── metrics.py        # Statistics collection
├── config/
│   ├── settings.py       # Bot configuration
│   └── constants.py      # Constants and messages
└── data/
    ├── presets.json      # Music presets
    └── languages.json    # Language configuration
```

### Running Tests
```bash
python -m pytest test_radio_bot.py -v
```

### Adding New Features
1. **Commands**: Add to `radio_cog.py`
2. **Presets**: Edit `data/presets.json`
3. **Languages**: Update `constants.py` and `languages.json`
4. **Settings**: Modify `config/settings.py`

## 🎵 Original ACE-Step Radio (Gradio)

This project also includes the original radio interface:

```bash
# Run original Gradio interface
python radio_gradio.py --port 7865
```

Features of the original interface:
- Web-based music generation
- Real-time streaming
- Multiple genre support
- Random mode with variations
- Station identity generation

See original README sections below for Gradio-specific features.

## 📄 License

This project inherits the license from [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step).

## 🙏 Acknowledgments

- **[ACE-Step Team](https://github.com/ace-step/ACE-Step)** - Original AI music generation model
- **[PasiKoodaa](https://github.com/PasiKoodaa/ACE-Step-RADIO)** - ACE-Step-RADIO base implementation  
- **[Discord.py](https://discordpy.readthedocs.io/)** - Discord API wrapper
- **[Llama.cpp](https://github.com/ggerganov/llama.cpp)** - LLM inference engine

## 🆘 Support

For issues and support:
1. Check [troubleshooting section](#🛠️-troubleshooting)
2. Review bot logs: `discord_radio.log`
3. Run tests: `python -m pytest test_radio_bot.py`
4. Open GitHub issue with logs and system info

---

## 📚 Additional Documentation

- **[Linux Setup Guide](docs/LINUX_SETUP.md)** - Comprehensive Linux installation guide
- **[Improvements & Roadmap](IMPROVEMENTS.md)** - Future features and suggestions
- **[Changelog](CHANGELOG.md)** - Version history and updates

---

**⚠️ Warning**: This bot requires significant computational resources. Recommended for use on dedicated servers with GPU acceleration.

---

# Original ACE-Step RADIO (Gradio Interface)

*Below is the original documentation for the Gradio web interface.*

---

https://github.com/user-attachments/assets/f733ebdb-7fe4-4812-b6b2-ac95e48bed55

UPDATE 11/5/2025: Major memory optimization achieved! RTX 3060 12GB can now stream songs continuously.

# Radio Station Feature Fork
 
 This fork introduces a **Radio Station** feature where AI generates continuous radio music. The process involves two key components:  
 - **LLM**: Generates the lyrics for the songs.  
 - **ACE**: Composes the music for the generated lyrics.
 

 If your computer struggles to stream songs continuously, increasing the buffer size will result in a longer initial delay but fewer gaps between songs (until the buffer is depleted again).


By default the app attempts to load the model file gemma-3-12b-it-abliterated.q4_k_m.gguf from the same directory. However, you can also use alternative LLMs. Note that the quality of generated lyrics will vary depending on the LLM's capabilities.
 
  ---
 
 ## Requirements
 
 To run this project, you need the `llama-cpp-python` library. Install it using the following command:
 
 ```bash
 pip install llama-cpp-python
 ```
### CPU vs GPU Usage
 
By default, `llama-cpp-python` uses the CPU for processing, which is suitable if you have limited VRAM. However, setting up GPU acceleration can significantly improve performance.
 
I successfully configured GPU support (on Windows) using:
- Python 3.11
- CUDA 12.8  
 
For more details on setting up GPU acceleration (on Windows), refer to the following resource:  
[llama-cpp-python-cu128-gemma3 Releases](https://github.com/boneylizard/llama-cpp-python-cu128-gemma3/releases)
 
---
### How to Launch the Application
Once your environment is set up, you can launch the application by running the following command:
```bash
python radio_gradio.py
```
