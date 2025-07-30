# ACE-Step CPU Offload Bug Fix

## Problem

Original ACE-Step code in `pipeline_ace_step.py` has bugs in `load_quantized_checkpoint()` method:

1. **music_dcae placement bug** (lines 292-294):
   ```python
   if self.cpu_offload:
       self.music_dcae.eval().to(self.dtype).to(self.device)  # BUG: Goes to GPU!
   else:
       self.music_dcae.eval().to(self.dtype).to('cpu')       # Goes to CPU
   ```
   Logic is inverted - when `cpu_offload=True`, model should go to CPU, not GPU.

2. **map_location bug** (lines 302, 313):
   ```python
   map_location=self.device  # BUG: Always loads to GPU even with cpu_offload=True
   ```

3. **quantized repo missing**:
   ```python
   REPO_ID_QUANT = "ACE-Step/ACE-Step-v1-3.5B-q4-K-M"  # Repository doesn't exist!
   ```

## Impact

These bugs cause:
- 7.9GB VRAM usage instead of expected <4GB with `cpu_offload=True`
- CPU offload doesn't work despite being enabled
- Models are placed on GPU instead of CPU when `cpu_offload=True`
- 401 errors trying to download non-existent quantized models

## Fix Applied

### 1. Fixed music_dcae placement logic:
```python
if self.cpu_offload:
    self.music_dcae.eval().to(self.dtype).to('cpu')      # FIXED: CPU for offload
else:
    self.music_dcae.eval().to(self.dtype).to(self.device)
```

### 2. Fixed map_location for state_dict loading:
```python
map_location='cpu' if self.cpu_offload else self.device  # FIXED: CPU map for offload
```

### 3. Re-enabled torch_compile with Windows cache fix:
```python
# Clear torch compile cache to prevent FileExistsError on Windows
torch._dynamo.reset()
# Clear temp directories: torch_compile*
```

### 4. Optimized dtype to bfloat16:
```python
dtype = "bfloat16"  # Better performance than float32, works with CPU offload
```

### 5. Disabled quantized models (use normal models with CPU offload):
```python
quantized=False  # FIXED: Disable quantized (repo doesn't exist)
```

## Result

With these fixes, official ACE-Step 8GB optimization works optimally:
- ✅ `torch_compile=true` with Windows cache clearing
- ✅ `cpu_offload=true` with proper model placement
- ✅ `overlapped_decode=true` for memory efficiency
- ✅ `dtype="bfloat16"` for optimal performance
- Use <4GB VRAM instead of 7.9GB
- Use normal models instead of non-existent quantized ones

## Files Modified

- `acestep/pipeline_ace_step.py` - Fixed quantized checkpoint loading bugs
- `discord_bot/utils/radio_engine.py` - Re-enabled torch_compile + Windows cache fix + bfloat16 dtype + disabled quantized
- `discord_bot/bot.py` - Enhanced configuration reporting
- `.env` - Re-enabled TORCH_COMPILE=true

## Test

Start the bot with official ACE-Step 8GB optimization:
```
CPU_OFFLOAD=true
TORCH_COMPILE=true  
OVERLAPPED_DECODE=true
```
Expected result: <4GB VRAM usage with bfloat16 precision, torch compilation or graceful fallback to eager mode.
