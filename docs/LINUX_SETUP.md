# 🐧 Linux Setup Guide for ACE-Step RADIO Discord BOT

Complete installation guide for Linux systems.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, Fedora 35+, or similar
- **RAM**: 16GB+ recommended
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3060/4060 or better)
- **Storage**: 20GB free space
- **Python**: 3.10+ (installed automatically by setup script)

### Required Software
1. **NVIDIA Drivers** (if using GPU)
2. **CUDA Toolkit** (installed by setup script)
3. **Conda/Miniconda** (required)
4. **FFmpeg** (for audio processing)
5. **Git** (for cloning repository)

## Installation Steps

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential

# Install FFmpeg
sudo apt install -y ffmpeg

# Verify FFmpeg installation
ffmpeg -version
```

#### Fedora
```bash
# Update system
sudo dnf update -y

# Install essential tools
sudo dnf install -y git curl wget gcc gcc-c++ make

# Install FFmpeg (enable RPM Fusion first)
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y ffmpeg

# Verify FFmpeg installation
ffmpeg -version
```

#### Arch Linux
```bash
# Update system
sudo pacman -Syu

# Install essential tools
sudo pacman -S git curl wget base-devel

# Install FFmpeg
sudo pacman -S ffmpeg

# Verify FFmpeg installation
ffmpeg -version
```

### 2. Install NVIDIA Drivers (if not already installed)

#### Ubuntu/Debian
```bash
# Check if drivers are installed
nvidia-smi

# If not installed, add NVIDIA PPA
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update

# Install latest driver (or specific version)
sudo apt install -y nvidia-driver-535  # or latest version

# Reboot
sudo reboot
```

#### Fedora
```bash
# Enable RPM Fusion repository
sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install NVIDIA drivers
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda

# Reboot
sudo reboot
```

### 3. Install Miniconda

```bash
# Download Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Make it executable
chmod +x Miniconda3-latest-Linux-x86_64.sh

# Run installer
bash Miniconda3-latest-Linux-x86_64.sh

# Follow prompts, accept license, choose install location
# When asked "Do you wish the installer to initialize Miniconda3", answer "yes"

# Reload shell configuration
source ~/.bashrc

# Verify installation
conda --version
```

### 4. Clone Repository

```bash
# Clone the repository
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT

# Checkout beta branch for latest features
git checkout beta
```

### 5. Run Setup Script

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

The setup script will:
- ✅ Check for Python and Conda
- ✅ Create conda environment `ace-radio`
- ✅ Install PyTorch with CUDA (tries 12.4 → 12.1 → 11.8)
- ✅ Install Discord bot dependencies
- ✅ Install ACE-Step
- ✅ Check for FFmpeg
- ✅ Create .env file template

### 6. Configure Environment

```bash
# Edit .env file
nano .env  # or vim .env or your preferred editor

# Set your Discord bot token
DISCORD_TOKEN=your_actual_token_here

# Optional: Set interface language (default: polish)
BOT_LANGUAGE=english  # or polish

# Optional: Enable CPU offload for 8GB VRAM GPUs
CPU_OFFLOAD=true
```

### 7. Activate Environment and Run

```bash
# Activate conda environment
conda activate ace-radio

# Run the bot
python discord_bot/bot.py
```

## Troubleshooting

### CUDA Not Found

If you get "CUDA not available" errors:

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA installation
nvcc --version

# If CUDA not found, install CUDA Toolkit
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-4

# Fedora
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/fedora37/x86_64/cuda-fedora37.repo
sudo dnf install -y cuda-toolkit-12-4
```

### Conda Command Not Found

If `conda` command is not recognized after installation:

```bash
# Add to PATH manually
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or initialize conda
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

### FFmpeg Not Found

```bash
# Ubuntu/Debian
sudo apt install -y ffmpeg

# Fedora (enable RPM Fusion first)
sudo dnf install -y ffmpeg

# Arch
sudo pacman -S ffmpeg

# Verify
which ffmpeg
ffmpeg -version
```

### Permission Denied Errors

If you get permission errors:

```bash
# Make sure you own the repository directory
sudo chown -R $USER:$USER ~/ACE-Step-RADIO-Discord-BOT

# Make scripts executable
chmod +x setup.sh
```

### Out of Memory Errors

If you get CUDA out of memory errors:

1. Edit `.env`:
   ```bash
   CPU_OFFLOAD=true
   DEFAULT_DURATION=60
   MAX_LENGTH_MAX=180
   ```

2. Restart bot:
   ```bash
   conda activate ace-radio
   python discord_bot/bot.py
   ```

### Bot Won't Start

```bash
# Check Discord token
grep DISCORD_TOKEN .env

# Check Python environment
conda list | grep discord

# Check logs
tail -f discord_radio.log  # if logging is enabled

# Test imports
python -c "import discord; print(discord.__version__)"
python -c "import torch; print(torch.cuda.is_available())"
```

## Performance Optimization

### For 8GB VRAM GPUs

Edit `.env`:
```bash
CPU_OFFLOAD=true
TORCH_COMPILE=true
OVERLAPPED_DECODE=true
DEFAULT_DURATION=60
LLM_GPU_LAYERS=-1
```

### For 12GB+ VRAM GPUs

Edit `.env`:
```bash
CPU_OFFLOAD=false
TORCH_COMPILE=false
DEFAULT_DURATION=120
LLM_GPU_LAYERS=-1
```

## Running as a Service

To run the bot as a systemd service:

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/ace-radio-bot.service
```

### 2. Add Configuration

```ini
[Unit]
Description=ACE-Step RADIO Discord Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ACE-Step-RADIO-Discord-BOT
Environment="PATH=/home/YOUR_USERNAME/miniconda3/envs/ace-radio/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/YOUR_USERNAME/miniconda3/envs/ace-radio/bin/python discord_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username.

### 3. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable ace-radio-bot

# Start service
sudo systemctl start ace-radio-bot

# Check status
sudo systemctl status ace-radio-bot

# View logs
sudo journalctl -u ace-radio-bot -f
```

## Updating

```bash
# Activate environment
conda activate ace-radio

# Pull latest changes
git pull origin beta

# Update dependencies
pip install -r requirements_discord.txt --upgrade

# Restart bot (if running as service)
sudo systemctl restart ace-radio-bot
```

## Uninstallation

```bash
# Stop service (if running)
sudo systemctl stop ace-radio-bot
sudo systemctl disable ace-radio-bot

# Remove conda environment
conda deactivate
conda env remove -n ace-radio

# Remove repository
cd ~
rm -rf ACE-Step-RADIO-Discord-BOT

# Optional: Remove Miniconda
rm -rf ~/miniconda3
```

## Additional Resources

- [Main README](../README.md)
- [Improvements Roadmap](../IMPROVEMENTS.md)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [NVIDIA CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)

## Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review bot logs
3. Check system resources (`nvidia-smi`, `htop`)
4. Open an issue on GitHub with:
   - Your Linux distribution and version
   - GPU model and VRAM
   - Error messages and logs
   - Steps to reproduce

---

**Good luck with your setup! 🎵**
