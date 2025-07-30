# LLM GPU Acceleration Setup

## New LLM Model: Huihui-gemma-3n-E4B-it-abliterated

**Model**: `mradermacher/Huihui-gemma-3n-E4B-it-abliterated-GGUF`
**Size**: Q4_K_M quantization (~2.3GB)
**Benefits**: 
- Smaller than previous Gemma-3-12B model  
- Better GPU fit with ACE-Step CPU offload
- Faster lyrics generation on GPU

## Configuration

### Smart GPU/CPU Allocation:

When `CPU_OFFLOAD=true` (8GB VRAM optimization):
- **ACE-Step**: CPU offload (~2-4GB VRAM) 
- **LLM**: GPU acceleration (remaining VRAM)
- **Result**: Best of both worlds

When `CPU_OFFLOAD=false` (>10GB VRAM):
- **ACE-Step**: Full GPU (~6-8GB VRAM)
- **LLM**: CPU mode (to avoid VRAM conflict)
- **Result**: Maximum ACE-Step performance

### Environment Variables (.env):

```env
# LLM Configuration
LLM_MODEL_NAME=Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf
LLM_GPU_LAYERS=-1  # -1 = all layers on GPU, 0 = CPU only

# ACE-Step Configuration  
CPU_OFFLOAD=true
TORCH_COMPILE=true
OVERLAPPED_DECODE=true
```

## Performance Comparison

| Configuration | ACE-Step | LLM | Total VRAM | Speed |
|---------------|----------|-----|------------|-------|
| **8GB Optimized** | CPU offload | GPU | ~4-6GB | Fast lyrics + Fast music |
| **Legacy** | Full GPU | CPU | ~8GB | Slow lyrics + Fast music |

## Automatic Download

The bot will automatically download the new model on first run:
- **URL**: `https://huggingface.co/mradermacher/Huihui-gemma-3n-E4B-it-abliterated-GGUF/resolve/main/Huihui-gemma-3n-E4B-it-abliterated.Q4_K_M.gguf`
- **Size**: ~2.3GB
- **Location**: `~/.cache/ace-step/checkpoints/`

## Monitoring

Bot startup will show:
```
🔥 LLM GPU acceleration enabled: -1 layers
💡 ACE-Step CPU offload + LLM GPU = optimal 8GB usage
```

Or when GPU not available:
```
💻 LLM CPU mode: ACE-Step has GPU priority
```

## Fallback

If new model fails to download or load, bot falls back to:
1. Any existing LLM model in cache
2. Fallback lyrics generation (built-in templates)
3. Full functionality maintained
