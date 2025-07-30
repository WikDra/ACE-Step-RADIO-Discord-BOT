# ⚡ VRAM Optimization for 8GB Systems

> **Specialized guide for optimizing ACE-Step RADIO Discord Bot on 8GB VRAM systems**

For complete setup instructions, see: [Setup Guide](./docs/SETUP.md)

## 🎯 8GB VRAM Strategy

The key to running ACE-Step on 8GB VRAM is **smart resource allocation**:

1. **ACE-Step**: CPU offload mode (~2-4GB VRAM)
2. **LLM**: GPU acceleration on remaining VRAM (~3-4GB)
3. **System**: Reserve 1-2GB for Discord/Windows

## ⚙️ Optimal Configuration

### Environment Settings (.env)
```properties
# 8GB VRAM Optimization
CPU_OFFLOAD=true           # ACE-Step uses CPU + minimal GPU
TORCH_COMPILE=true         # Official 8GB optimization
OVERLAPPED_DECODE=true     # Improved memory efficiency

# LLM Settings
LLM_GPU_LAYERS=-1          # Use remaining GPU memory
LLM_MODEL_NAME=Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf

# Performance Tuning
DEFAULT_DURATION=60        # Shorter tracks = less memory
MAX_LENGTH_MAX=300         # Allow up to 5-minute tracks
```

### CUDA Setup (Windows)
```bash
# Run setup with Administrator privileges
setup.bat  # Installs CUDA 12.4 with fallbacks

# Manual CUDA installation order:
# 1. Try CUDA 12.4 (best optimization)
# 2. Fallback to CUDA 12.1 (good compatibility) 
# 3. Fallback to CUDA 11.8 (maximum compatibility)
```

## 📊 Memory Usage Breakdown

| Component | No Optimization | With CPU Offload | Savings |
|-----------|----------------|------------------|---------|
| **ACE-Step Pipeline** | ~7.9GB | ~2-4GB | 4-6GB ✅ |
| **LLM (Huihui-gemma)** | ~4GB | ~3GB | 1GB ✅ |
| **System/Discord** | ~1GB | ~1GB | 0GB |
| **Total** | **~13GB** ❌ | **~6-8GB** ✅ | **5-7GB** |

## 🔧 CPU Offload Technical Details

### What CPU Offload Does
- **Model weights**: Kept on CPU memory
- **Computations**: GPU kernels when needed
- **Music_dcae**: Forced to CPU (fixed bug)
- **Memory allocation**: Fixed `map_location='cpu'`

### Performance Impact
- **Generation time**: 8-15 seconds (vs 5-8 seconds full GPU)
- **Quality**: Identical output
- **Stability**: Better for 8GB systems
- **Power usage**: Slightly higher CPU usage

### Fixed Bugs in CPU Offload
1. **music_dcae placement** - Was incorrectly staying on GPU
2. **Quantized checkpoint loading** - Fixed map_location for CPU
3. **Memory cleanup** - Proper torch.cuda.empty_cache()

## 🚀 Performance Optimization

### 1. GPU Memory Monitoring
```bash
# Monitor VRAM usage in real-time
watch -n 1 nvidia-smi

# Expected usage during generation:
# - Idle: 0.1-0.5GB
# - Loading: 2-4GB  
# - Generating: 4-6GB
# - Peak: 6-8GB (should not exceed)
```

### 2. Bot Commands for Memory Management
```bash
# Check current settings
/radio_settings

# Optimize for memory
/radio_maxlength 60        # Shorter tracks
/radio_auto false          # Manual queue control

# Check performance
/radio_stats              # Shows generation times
```

### 3. Advanced Tuning
```properties
# Further memory reduction (if needed)
BATCH_SIZE=1              # Smaller batches
BUFFER_SIZE=2             # Smaller queue buffer

# Disable features for extreme memory savings
LLM_GPU_LAYERS=0          # LLM on CPU only
TORCH_COMPILE=false       # Disable optimizations
```

## 🛠️ Troubleshooting

### "CUDA out of memory" Errors
```bash
# Solution 1: Verify CPU offload is enabled
grep CPU_OFFLOAD .env
# Should show: CPU_OFFLOAD=true

# Solution 2: Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"

# Solution 3: Restart bot to reset memory
```

### High Memory Usage Despite CPU Offload
```bash
# Check if fixes are applied
grep -n "music_dcae.*cpu" discord_bot/utils/radio_engine.py
grep -n "map_location.*cpu" acestep/pipeline_ace_step.py

# If missing, re-run setup or manual fixes
```

### Slow Generation Times
```bash
# Normal CPU offload times:
# 60s track: 8-15 seconds
# 120s track: 15-25 seconds  
# 300s track: 30-45 seconds

# If much slower, check:
# 1. CPU performance
# 2. System RAM availability
# 3. SSD vs HDD storage
```

## 🎯 GPU Compatibility Matrix

| GPU Model | VRAM | Recommended Mode | Performance |
|-----------|------|------------------|-------------|
| **RTX 4060 Laptop** | 8GB | CPU Offload + LLM GPU | 🔥 Excellent |
| **RTX 3060** | 8GB/12GB | CPU Offload + LLM GPU | 🚀 Very Good |
| **RTX 4060** | 8GB | CPU Offload + LLM GPU | 🔥 Excellent |
| **RTX 3070** | 8GB | CPU Offload + LLM GPU | 🚀 Very Good |
| **RTX 2070 Super** | 8GB | CPU Offload, LLM CPU | ⚡ Good |
| **GTX 1070 Ti** | 8GB | CPU Offload, LLM CPU | ⚠️ Basic |

## 📈 Benchmark Results

### RTX 4060 Laptop 8GB + CPU Offload
- **60s track**: 8-12 seconds
- **120s track**: 15-20 seconds
- **Peak VRAM**: 6.2GB
- **Quality**: Perfect
- **Stability**: 100% reliable

### Comparison: Full GPU vs CPU Offload
| Metric | Full GPU (12GB) | CPU Offload (8GB) | Difference |
|--------|-----------------|-------------------|------------|
| **Generation Speed** | 5-8s | 8-15s | ~2x slower |
| **VRAM Usage** | 7.9GB | 6.2GB | 22% reduction |
| **Quality** | Perfect | Perfect | Identical |
| **Stability** | Good | Excellent | Better |

## 🔮 Future Optimizations

### Planned Improvements
- **Dynamic memory allocation** - Adjust based on available VRAM
- **Mixed precision training** - Further memory reduction
- **Model quantization** - 4-bit/8-bit inference
- **Streaming generation** - Process in chunks

### Experimental Features
- **Multi-GPU support** - Distribute ACE-Step and LLM
- **CPU-GPU streaming** - Overlap computation and transfer
- **Adaptive quality** - Reduce quality for memory savings

---

> **💡 Pro Tip**: The 8GB optimization actually provides better stability than full GPU mode, making it the recommended setup even for higher VRAM systems.

> **⚠️ Note**: CPU offload requires good CPU performance. Ensure your system has adequate cooling for sustained loads.
