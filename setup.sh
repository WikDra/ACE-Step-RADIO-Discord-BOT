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

# CUDA versions to try (in order of preference)
CUDA_VERSION_PRIMARY="12.4"
CUDA_VERSION_SECONDARY="12.1"
CUDA_VERSION_LEGACY="11.8"

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

echo "[1/8] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found! Please install Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

echo "[2/8] Checking Conda..."
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
echo "[3/8] Checking Python environment..."
if conda env list | grep -q "ace-radio"; then
    echo -e "${GREEN}✅ Environment ace-radio already exists${NC}"
else
    echo "Creating new Conda environment..."
    conda create -n ace-radio python=3.10 -y
fi

echo "[4/8] Installing PyTorch with CUDA..."
echo "🔧 Detecting GPU and installing appropriate CUDA version..."

# Try CUDA versions in order of preference
echo "Attempting CUDA ${CUDA_VERSION_PRIMARY} installation..."
if conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=${CUDA_VERSION_PRIMARY} -c pytorch -c nvidia -y; then
    echo -e "${GREEN}✅ CUDA ${CUDA_VERSION_PRIMARY} installed successfully - optimal for RTX 30xx/40xx${NC}"
else
    echo -e "${YELLOW}⚠️ CUDA ${CUDA_VERSION_PRIMARY} installation failed, trying CUDA ${CUDA_VERSION_SECONDARY}...${NC}"
    if conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=${CUDA_VERSION_SECONDARY} -c pytorch -c nvidia -y; then
        echo -e "${GREEN}✅ CUDA ${CUDA_VERSION_SECONDARY} installed - good optimization for RTX 30xx/40xx${NC}"
    else
        echo -e "${YELLOW}⚠️ CUDA ${CUDA_VERSION_SECONDARY} failed, trying legacy CUDA ${CUDA_VERSION_LEGACY}...${NC}"
        echo "💡 CUDA ${CUDA_VERSION_LEGACY} is for older GPUs (GTX 10xx, RTX 20xx)"
        if conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=${CUDA_VERSION_LEGACY} -c pytorch -c nvidia -y; then
            echo -e "${GREEN}✅ CUDA ${CUDA_VERSION_LEGACY} installed - CPU offload will work but slower${NC}"
        else
            echo -e "${RED}❌ All CUDA installations failed!${NC}"
            echo -e "${YELLOW}Falling back to CPU-only PyTorch...${NC}"
            conda install -n ace-radio pytorch torchvision torchaudio cpuonly -c pytorch -y
            echo -e "${YELLOW}⚠️ CPU-only mode installed - will be slow, GPU recommended${NC}"
        fi
    fi
fi

echo "[5/8] Installing Discord bot dependencies..."
conda run -n ace-radio pip install -r requirements_discord.txt

echo "[6/8] Installing ACE-Step..."
conda run -n ace-radio pip install -e .

echo "[7/8] Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️ FFmpeg not found!${NC}"
    echo "Install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
    echo "  Arch: sudo pacman -S ffmpeg"
else
    # Safely extract ffmpeg version
    FFMPEG_VERSION=$(ffmpeg -version 2>/dev/null | head -n1 | cut -d' ' -f3 || echo "unknown")
    echo -e "${GREEN}✅ FFmpeg found (version: ${FFMPEG_VERSION})${NC}"
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
