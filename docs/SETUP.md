# 🔧 Setup & Installation Guide

Complete setup guide for ACE-Step RADIO Discord Bot on Windows and Linux.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11 or Ubuntu 20.04+
- **Python**: 3.10 or 3.11 (3.12 not fully supported)
- **CUDA**: 11.8+ (for GPU acceleration)
- **RAM**: 16GB+ system memory
- **Storage**: 20GB+ free space

### GPU Requirements
| VRAM | Mode | Performance | Notes |
|------|------|-------------|-------|
| 4-6GB | CPU Offload | Slower but functional | GTX 1060, RTX 2060 |
| 8GB | CPU Offload + Optimizations | Good performance | **RTX 4060 Laptop (recommended)** |
| 12GB+ | Full GPU | Maximum speed | RTX 3080, RTX 4080+ |

## 🚀 Automated Setup (Windows)

### Option 1: One-Click Setup
```bash
# Clone and run setup
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT
setup.bat  # Run as Administrator for symlinks
```

The `setup.bat` script will:
- ✅ Install Miniconda (if needed)
- ✅ Create `ace-radio` conda environment
- ✅ Install CUDA cascading (12.4 → 12.1 → 11.8)
- ✅ Install all Python dependencies
- ✅ Setup optimizations for 8GB VRAM

### Option 2: Advanced Setup
```bash
# For manual CUDA control
setup_advanced_pip.bat
```

## 🐧 Manual Setup (Linux/Advanced)

### 1. Install Conda
```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

### 2. Create Environment
```bash
# Create Python 3.10 environment
conda create -n ace-radio python=3.10
conda activate ace-radio
```

### 3. Install CUDA (GPU users)
```bash
# Install CUDA 12.4 (recommended)
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

# Alternative: CUDA 11.8 for older GPUs
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### 4. Install Dependencies
```bash
# Discord bot dependencies
pip install -r requirements_discord.txt

# Alternative: Core ACE-Step only
pip install -r requirements.txt
```

### 5. Install LLM Support (Optional)
```bash
# For GPU acceleration (if VRAM allows)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# For CPU only
pip install llama-cpp-python
```

## ⚙️ Configuration

### 1. Discord Bot Setup

1. **Create Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Go to "Bot" section
   - Copy the token

2. **Set Bot Permissions:**
   - Enable "Send Messages"
   - Enable "Connect" and "Speak" (for voice)
   - Generate invite link with permissions

3. **Configure Environment:**
   ```bash
   # Copy template
   cp .env.example .env
   
   # Edit .env file
   nano .env  # or notepad .env on Windows
   ```

### 2. Environment Variables

```properties
# REQUIRED: Discord Bot Token
DISCORD_TOKEN=OTU0NTAyNDYzMjc5NDgwOTAz.Gc-Ks9...

# PERFORMANCE: 8GB VRAM Optimization
CPU_OFFLOAD=true
TORCH_COMPILE=true
OVERLAPPED_DECODE=true

# AUDIO: Default Settings
DEFAULT_DURATION=60
MAX_LENGTH_MAX=300

# LLM: GPU Acceleration (if VRAM allows)
LLM_MODEL_NAME=Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf
LLM_GPU_LAYERS=-1  # -1 = all layers on GPU, 0 = CPU only
```

### 3. VRAM Optimization Profiles

#### 8GB VRAM (RTX 4060 Laptop) - Recommended
```properties
CPU_OFFLOAD=true           # ACE-Step on CPU (~2-4GB VRAM)
TORCH_COMPILE=true         # 8GB optimization
LLM_GPU_LAYERS=-1          # LLM on GPU (remaining VRAM)
```

#### 12GB+ VRAM (High Performance)
```properties
CPU_OFFLOAD=false          # ACE-Step on GPU (~7-8GB VRAM)
TORCH_COMPILE=true         # Performance boost
LLM_GPU_LAYERS=0           # LLM on CPU (or secondary GPU)
```

#### 4-6GB VRAM (Compatibility)
```properties
CPU_OFFLOAD=true           # ACE-Step on CPU
TORCH_COMPILE=false        # Disable optimizations
LLM_GPU_LAYERS=0           # LLM on CPU only
```

## 🏃 Running the Bot

### 1. Start Bot
```bash
# Activate environment
conda activate ace-radio

# Run bot (from project root)
python discord_bot/bot.py
```

### 2. First Run
The bot will automatically:
- ✅ Download ACE-Step model (~3GB)
- ✅ Download LLM model (~4GB, if enabled)
- ✅ Create output directories
- ✅ Initialize Discord connection

### 3. Test Bot
```bash
# In Discord, use:
/radio_help     # Show all commands
/radio_join     # Join voice channel
/radio_play     # Generate first song
```

## 🔧 Troubleshooting

### Common Issues

#### "CUDA out of memory"
```properties
# Solution 1: Enable CPU offload
CPU_OFFLOAD=true

# Solution 2: Reduce LLM GPU usage
LLM_GPU_LAYERS=0

# Solution 3: Reduce batch size
BATCH_SIZE=1
```

#### "llama-cpp-python has no CUDA support"
```bash
# Reinstall with CUDA
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

#### "FFmpeg not found"
```bash
# Windows: Install via conda
conda install ffmpeg

# Linux: Install via package manager
sudo apt install ffmpeg  # Ubuntu
sudo dnf install ffmpeg  # Fedora
```

#### Bot connects but no audio
```bash
# Check Discord permissions
# Ensure bot has "Connect" and "Speak" permissions in voice channel

# Check audio format
# Bot uses WAV format - ensure Discord supports it
```

### Performance Issues

#### Slow generation (>30s per track)
1. **Enable optimizations:**
   ```properties
   CPU_OFFLOAD=true
   TORCH_COMPILE=true
   ```

2. **Check GPU usage:**
   ```bash
   nvidia-smi  # Monitor VRAM usage
   ```

3. **Reduce track length:**
   ```bash
   /radio_maxlength 60  # Shorter tracks = faster generation
   ```

#### Bot crashes on startup
1. **Check logs:**
   ```bash
   tail -f discord_radio.log
   ```

2. **Verify environment:**
   ```bash
   conda activate ace-radio
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Test minimal setup:**
   ```bash
   python -c "from discord_bot.bot import *"
   ```

## 📊 Monitoring & Logs

### Log Files
- `discord_radio.log` - Bot operation logs
- `bot_metrics.json` - Performance metrics
- `bot_statistics.json` - Usage statistics

### Performance Monitoring
```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Bot statistics
/radio_stats  # In Discord

# Queue status
/radio_settings  # In Discord
```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python discord_bot/bot.py
```

## 🔄 Updates & Maintenance

### Update Bot
```bash
# Pull latest changes
git pull origin main

# Update dependencies
conda activate ace-radio
pip install -r requirements_discord.txt --upgrade
```

### Update ACE-Step Model
```bash
# Force model re-download
rm -rf ~/.cache/ace-step/checkpoints/
python discord_bot/bot.py  # Will re-download
```

### Clean Temp Files
```bash
# Windows
./cleanup_temp.bat

# Linux
rm -rf ace_temp/ ace_discord_output/
```

---

> **💡 Tip**: For best performance on 8GB systems, use CPU offload mode and monitor VRAM usage with `nvidia-smi`.

> **⚠️ Note**: First run will download ~7GB of models. Ensure stable internet connection.
