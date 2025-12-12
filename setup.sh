#!/bin/bash

# ACE-Step Discord Radio Setup for Linux
# This script sets up the bot environment using Conda

set -e  # Exit on error

echo "🎵 ACE-Step Discord Radio Setup (Linux)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "radio_gradio.py" ]; then
    echo -e "${RED}❌ Error: radio_gradio.py not found!${NC}"
    echo "Make sure you're in the ACE-Step-RADIO directory"
    exit 1
fi

# Check if discord_bot directory exists
if [ ! -d "discord_bot" ]; then
    echo -e "${RED}❌ Error: discord_bot directory not found!${NC}"
    echo "Create the Discord bot structure first"
    exit 1
fi

echo "[1/7] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found! Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

echo "[2/7] Checking Conda..."
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ ERROR: Conda not found!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️ IMPORTANT: This project requires Conda for proper PyTorch with CUDA installation${NC}"
    echo ""
    echo "📥 Install Miniconda:"
    echo "   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    echo "   bash Miniconda3-latest-Linux-x86_64.sh"
    echo ""
    echo "🔄 After installation, restart your terminal and run this script again"
    exit 1
fi
echo -e "${GREEN}✅ Conda found${NC}"

# Check if environment exists
echo "[3/7] Checking Python environment..."
if conda env list | grep -q "ace-radio"; then
    echo -e "${GREEN}✅ Environment ace-radio already exists${NC}"
else
    echo "Creating new Conda environment..."
    conda create -n ace-radio python=3.10 -y
fi

echo "[4/7] Installing PyTorch with CUDA..."
echo "🔧 Detecting GPU and installing appropriate CUDA version..."

# Try CUDA 12.4 first (best for RTX 30xx/40xx)
echo "Attempting CUDA 12.4 installation..."
if conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia -y; then
    echo -e "${GREEN}✅ CUDA 12.4 installed successfully - optimal for RTX 30xx/40xx${NC}"
else
    echo -e "${YELLOW}⚠️ CUDA 12.4 installation failed, trying CUDA 12.1...${NC}"
    if conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y; then
        echo -e "${GREEN}✅ CUDA 12.1 installed - good optimization for RTX 30xx/40xx${NC}"
    else
        echo -e "${YELLOW}⚠️ CUDA 12.1 failed, trying legacy CUDA 11.8...${NC}"
        echo "💡 CUDA 11.8 is for older GPUs (GTX 10xx, RTX 20xx)"
        conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
        echo -e "${GREEN}✅ CUDA 11.8 installed - CPU offload will work but slower${NC}"
    fi
fi

echo "[5/7] Installing Discord bot dependencies..."
conda run -n ace-radio pip install -r requirements_discord.txt

echo "[6/7] Installing ACE-Step..."
conda run -n ace-radio pip install -e .

echo "[7/7] Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️ FFmpeg not found!${NC}"
    echo "Install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
    echo "  Arch: sudo pacman -S ffmpeg"
else
    echo -e "${GREEN}✅ FFmpeg found: $(ffmpeg -version | head -n1)${NC}"
fi

echo ""
echo "[8/8] Configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "DISCORD_TOKEN=YOUR_TOKEN_HERE" > .env
    echo ""
    echo -e "${YELLOW}⚠️ IMPORTANT: Set your Discord token in .env file${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup completed!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env and set your DISCORD_TOKEN"
echo "2. Download ACE-Step models (if you haven't already)"
echo "3. Activate environment: conda activate ace-radio"
echo "4. Run the bot: python discord_bot/bot.py"
echo ""
echo "🔧 Environment activation:"
echo "   conda activate ace-radio"
echo ""
echo "💡 For 8GB VRAM GPUs, set CPU_OFFLOAD=true in .env"
echo ""
