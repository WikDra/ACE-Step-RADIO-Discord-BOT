# 🚀 VRA- **CUDA**: 12.6+ (for 8GB VRAM optimizations) Optimization Guide

## Problem: Bot używa 13GB| Mode | VRAM Usage | Performanc1. **Update setup.bat** ✅ - Upgraded to CUDA 12.4 (cascading fallback: 12.4→12.1→11.8)
2. **Run as Admin** - User needs to restart setup.bat as Administrator  
3. **Test VRAM usage** - Should drop from 13GB to 6-8GB
4. **Monitor performance** - CPU offload = slower but 8GB compatible

**Note**: CUDA 12.6/12.8 not yet available in conda repositoriesGPU Target |
|------|------------|-------------|-------------|
| **CUDA 12.4 + CPU Offload** | 6-8GB | 🔥 Best | RTX 3060+, RTX 40xx |
| **CUDA 12.1 + CPU Offload** | 6-8GB | 🚀 Good | RTX 3060+, RTX 40xx |
| **CUDA 11.8 + CPU Offload** | 6-8GB | ⚠️ Slower | GTX 10xx, RTX 20xx |
| **Full CUDA (any version)** | 10-13GB | 🔥 Maximum speed | High VRAM cards | zamiast 8GB

### Root Cause Analysis

Bot poprawnie przekazuje `cpu_offload=True` do ACE-Step pipeline, ale optymalizacje nie działają z powodu:

1. **CUDA Version**: Używamy CUDA 11.8, a najnowsze optymalizacje wymagają 12.4+
2. **Windows Admin**: Symlinks w HuggingFace cache wymagają uprawnień administratora
3. **torch.compile**: Nie działa stabilnie na Windows z CUDA 11.8

### Current Settings ✅

```python
# discord_bot/config/settings.py - POPRAWNE
CPU_OFFLOAD = True
TORCH_COMPILE = False  
OVERLAPPED_DECODE = True

# discord_bot/cogs/radio_cog.py - POPRAWNE
radio_engine = RadioEngine(cpu_offload=CPU_OFFLOAD)

# discord_bot/utils/radio_engine.py - POPRAWNE  
self.pipeline = ACEStepPipeline.from_pretrained(
    "stepfun-ai/ACE-Step-v1-3.5B",
    torch_dtype=torch.float16,
    device="cuda",
    cpu_offload=cpu_offload  # ✅ Przekazujemy poprawnie
)
```

## Solutions 🔧

### 1. Upgrade CUDA (NAJWAŻNIEJSZE)

```bash
# setup.bat - AUTOMATYCZNE z cascading fallback
# Próbuje CUDA 12.4 → 12.1 → 11.8 (w tej kolejności)
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia -y

# Dostępne wersje w conda (stan: lipiec 2025):
# CUDA 12.4 - latest, best optimization for RTX 30xx/40xx
# CUDA 12.1 - stable, good optimization  
# CUDA 11.8 - legacy, dla starych kart GPU

# CUDA 12.6/12.8 - jeszcze niedostępne w conda
```

**Dlaczego CUDA 12.4+?**
- ACE-Step @cpu_offload decorators wymagają nowszego CUDA
- torch.compile stabilność na Windows  
- Lepsze zarządzanie pamięcią GPU
- Wsparcie dla newest cudnn optimizations

**Legacy CUDA 11.8**:
- ✅ Działa z ACE-Step na starych kartach GPU
- ✅ CPU offload redukuje VRAM do ~8GB (ale wolniej)
- 💡 Użyj dla GTX 1060/1070/1080, RTX 2060/2070 
- ⚠️ Nowsze karty (RTX 3060+) powinny używać CUDA 12.4

### 2. Windows Admin Privileges

```bash
# Uruchom setup.bat jako Administrator
# Prawy klik → "Uruchom jako administrator"
```

**Dlaczego admin?**
- HuggingFace tworzy symlinks w ~/.cache/
- Windows blokuje symlinks bez admin
- ACE-Step model loading potrzebuje symlinks
- torch.compile cache wymaga pełnych uprawnień

### 3. Verification Commands

```bash
# Sprawdź CUDA version
python -c "import torch; print(torch.version.cuda)"

# Sprawdź VRAM usage  
nvidia-smi

# Test CPU offload
python -c "
import torch
from acestep.pipeline_ace_step import ACEStepPipeline
pipe = ACEStepPipeline.from_pretrained('stepfun-ai/ACE-Step-v1-3.5B', cpu_offload=True)
print('CPU offload enabled successfully')
"
```

## Expected Results 📊

| CUDA Version | VRAM Usage | CPU Offload | Performance | GPU Support |
|--------------|------------|-------------|-------------|-------------|
| **CUDA 11.8** | 6-8GB | ✅ Working (slower) | ⚠️ Legacy speed | GTX 10xx, RTX 20xx |
| **CUDA 12.1** | 6-8GB | ✅ Working (good) | 🚀 Good optimization | RTX 30xx, RTX 40xx |
| **CUDA 12.4** | 6-8GB | ✅ Working (best) | � Best optimization | RTX 30xx, RTX 40xx |
| **Full CUDA** | 10-13GB | ❌ Disabled | 🔥 Fastest | All modern GPUs |

### Mode Comparison

| Mode | VRAM Usage | Performance | GPU Target |
|------|------------|-------------|-------------|
| **CUDA 12.6 + CPU Offload** | 6-8GB | 🚀 Fast | RTX 3060+, RTX 40xx |
| **CUDA 11.8 + CPU Offload** | 6-8GB | ⚠️ Slower | GTX 10xx, RTX 20xx |
| **Full CUDA (any version)** | 10-13GB | � Fastest | High VRAM cards |

## ACE-Step CPU Offload Implementation

```python
# acestep/cpu_offload.py
@cpu_offload
def get_text_embeddings(self, text_input):
    # Model temporarily moved to GPU, then back to CPU
    
@cpu_offload  
def text2music_diffusion_process(self, latents):
    # Diffusion on GPU, offload after each step
    
@cpu_offload
def latents2audio(self, latents): 
    # Vocoder GPU processing, immediate offload
```

**Kluczowe**: Te decorators działają najlepiej z CUDA 12.4+, ale też z 12.1 na Windows!

## Next Steps 🎯

1. **Update setup.bat** ✅ - Upgraded to CUDA 12.4
2. **Run as Admin** - User needs to restart setup.bat as Administrator  
3. **Test VRAM usage** - Should drop from 13GB to 6-8GB
4. **Monitor performance** - CPU offload = slower but 8GB compatible

## Troubleshooting

### Still using 13GB after upgrade?

```bash
# Clear old CUDA cache
pip cache purge
conda clean --all

# Reinstall PyTorch with new CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

### CUDA 12.4 installation fails?

```bash
# Cascading fallback już wbudowany w setup.bat:
# 1. CUDA 12.4 (optimal)
# 2. CUDA 12.1 (good)  
# 3. CUDA 11.8 (legacy dla starych GPU)

# Manual installation if needed:
conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# CUDA 12.1 też wspiera CPU offload:
# - ✅ Reduces VRAM to 6-8GB 
# - 🚀 Good performance  
# - 💡 Stable dla RTX 30xx/40xx cards
```

### torch.compile errors?

```bash
# Disable torch.compile if unstable
# .env file:
TORCH_COMPILE=false
```

### Import errors after CUDA upgrade?

```bash
# Rebuild conda environment
conda env remove -n ace-radio
python setup.bat  # as Administrator
```
