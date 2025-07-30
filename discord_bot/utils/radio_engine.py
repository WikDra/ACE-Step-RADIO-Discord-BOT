"""
RadioEngine - Adaptacja radio_gradio.py dla Discord Bot
"""

import asyncio
import torch
import subprocess
import os
import time
import gc
import uuid
from pathlib import Path
from typing import Optional, Tuple
from llama_cpp import Llama

# Import from ACE-Step
from acestep.pipeline_ace_step import ACEStepPipeline
from acestep.schedulers import FlowMatchEulerDiscreteScheduler

# Local imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from discord_bot.config.settings import *

class RadioEngine:
    def __init__(self, checkpoint_path: str = None, cpu_offload: bool = False):
        """
        Inicjalizacja RadioEngine bazująca na radio_gradio.py
        
        Args:
            checkpoint_path: Ścieżka do modeli ACE-Step
            cpu_offload: Czy włączyć CPU offload (GPU+CPU hybryda)
        """
        # Setup paths
        self.output_dir = OUTPUT_DIR
        self.cache_dir = CACHE_DIR
        self.temp_dir = TEMP_DIR
        
        # Create directories if they don't exist
        for dir_path in [self.output_dir, self.cache_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self.checkpoint_path = checkpoint_path or str(ACE_CHECKPOINT_PATH)
        self.cpu_offload = cpu_offload
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        
        # Model instances (will be loaded on demand)
        self.llm = None
        self.ace_pipeline = None
        
        print(f"RadioEngine initialized - Device: {self.device}, CPU Offload: {cpu_offload}")
    
    def _load_llm(self) -> None:
        """Załaduj LLM Llama model"""
        if self.llm is None:
            print("Loading LLM model...")
            try:
                model_path = str(LLM_MODEL_PATH)
                self.llm = Llama(
                    model_path=model_path,
                    n_ctx=LLM_CONTEXT_SIZE,
                    n_gpu_layers=LLM_GPU_LAYERS if not self.cpu_offload else 0,
                    verbose=False,
                    seed=-1  # Random seed for variety
                )
                print(f"LLM loaded from: {model_path}")
            except Exception as e:
                print(f"Failed to load LLM: {e}")
                self.llm = None
    
    def _unload_llm(self) -> None:
        """Zwolnij LLM z pamięci"""
        if self.llm is not None:
            print("Unloading LLM model...")
            del self.llm
            self.llm = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def _load_ace_pipeline(self) -> ACEStepPipeline:
        """Załaduj ACE-Step Pipeline"""
        if self.ace_pipeline is None:
            print("Loading ACE-Step Pipeline...")
            
            # Try with torch_compile first, fallback to eager mode if it fails
            torch_compile_enabled = TORCH_COMPILE
            
            # Clear torch compile cache to prevent FileExistsError on Windows  
            if torch_compile_enabled:
                try:
                    import torch._dynamo
                    
                    # For Windows: Set suppress_errors to enable graceful fallback to eager
                    torch._dynamo.config.suppress_errors = True
                    torch._dynamo.config.verbose = False
                    
                    # Set cache environment for better Windows compatibility
                    os.environ['TORCH_COMPILE_DEBUG'] = '0'
                    os.environ['TORCHDYNAMO_CACHE_SIZE_LIMIT'] = '1'
                    
                    # Create unique temp directory for this session
                    session_id = str(uuid.uuid4())[:8]
                    temp_cache_dir = self.temp_dir / f"torch_cache_{session_id}"
                    temp_cache_dir.mkdir(exist_ok=True)
                    os.environ['TORCHINDUCTOR_CACHE_DIR'] = str(temp_cache_dir)
                    
                    print(f"🔧 torch_compile setup: suppress_errors=True, cache_dir={temp_cache_dir}")
                    
                except Exception as e:
                    print(f"⚠️ torch_compile setup failed: {e}")
                    torch_compile_enabled = False  # Disable if setup fails
            
            try:
                print(f"🔧 Initializing ACE-Step Pipeline with cpu_offload={self.cpu_offload}")
                print(f"🔧 Using torch_compile={torch_compile_enabled} (Official ACE-Step 8GB optimization)")
                if torch_compile_enabled:
                    print(f"💡 torch_compile enabled with suppress_errors=True (graceful Windows fallback)")
                # Use bfloat16 for better performance (works with CPU offload too)
                dtype = "bfloat16"
                print(f"🔧 Using dtype: {dtype}")
                print(f"🔧 FIXED: ACE-Step quantized CPU offload bugs + disabled quantized (repo missing)")
                
                self.ace_pipeline = ACEStepPipeline(
                    checkpoint_dir=self.checkpoint_path,
                    dtype=dtype,
                    torch_compile=torch_compile_enabled,  # Use official recommendation
                    cpu_offload=self.cpu_offload,  # Pass CPU offload setting
                    quantized=False,  # FIXED: Disable quantized (repo doesn't exist)
                    overlapped_decode=OVERLAPPED_DECODE  # Official 8GB VRAM optimization
                )
                print(f"✅ ACE-Step Pipeline loaded - CPU offload: {self.ace_pipeline.cpu_offload}")
            except Exception as e:
                if torch_compile_enabled and TORCH_COMPILE_FALLBACK:
                    print(f"⚠️ torch_compile failed ({e}), falling back to eager mode...")
                    print(f"💡 This is normal on Windows - CPU offload + eager mode still provides 8GB optimization")
                    
                    # Retry without torch_compile
                    print(f"🔧 Retrying ACE-Step Pipeline with cpu_offload={self.cpu_offload} (eager mode)")
                    print(f"🔧 Using torch_compile=False (Windows fallback)")
                    # Use bfloat16 for better performance (works with CPU offload too)
                    dtype = "bfloat16"
                    print(f"🔧 Using dtype: {dtype}")
                    print(f"🔧 FIXED: ACE-Step quantized CPU offload bugs + disabled quantized (repo missing)")
                    
                    self.ace_pipeline = ACEStepPipeline(
                        checkpoint_dir=self.checkpoint_path,
                        dtype=dtype,
                        torch_compile=False,  # Disabled for Windows compatibility
                        cpu_offload=self.cpu_offload,
                        quantized=False,  # FIXED: Disable quantized (repo doesn't exist)
                        overlapped_decode=OVERLAPPED_DECODE
                    )
                    print(f"✅ ACE-Step Pipeline loaded in eager mode - CPU offload: {self.ace_pipeline.cpu_offload}")
                else:
                    raise
        return self.ace_pipeline
    
    def _unload_ace_pipeline(self) -> None:
        """Zwolnij ACE-Step Pipeline z pamięci"""
        if self.ace_pipeline is not None:
            print("Unloading ACE-Step Pipeline...")
            del self.ace_pipeline
            self.ace_pipeline = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def _clean_all_memory(self) -> None:
        """Agresywne czyszczenie pamięci"""
        self._unload_llm()
        self._unload_ace_pipeline()
        
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
        
        # Clean torch compile cache
        try:
            torch_cache_dirs = list(self.temp_dir.glob("torch_cache_*"))
            for cache_dir in torch_cache_dirs:
                import shutil
                shutil.rmtree(cache_dir, ignore_errors=True)
        except:
            pass
        
        # Multiple GC passes
        for _ in range(3):
            gc.collect()
    
    def _generate_lyrics_sync(self, prompt: str) -> str:
        """Synchroniczne generowanie tekstów"""
        try:
            self._load_llm()
            if self.llm:
                response = self.llm(
                    prompt,
                    max_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    repeat_penalty=1.1,
                    stop=["[End]", "\n\n\n"],
                    echo=False
                )
                return response["choices"][0]["text"].strip()
            else:
                return self._fallback_lyrics(prompt)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._fallback_lyrics(prompt)
        finally:
            self._unload_llm()
    
    def _fallback_lyrics(self, prompt: str) -> str:
        """Fallback lyrics gdy LLM nie działa"""
        return (
            "[Verse 1]\n"
            "Generated by AI for you\n"
            "Music created just in time\n"
            "Digital dreams coming true\n"
            "Every beat and every rhyme\n\n"
            "[Chorus]\n"
            "This is our digital song\n"
            "Made by circuits and code\n"
            "Nothing here can go wrong\n"
            "In this electronic mode\n\n"
            "[Verse 2]\n"
            "Artificial but still real\n"
            "Every note designed with care\n"
            "This is how the future feels\n"
            "Music floating in the air"
        )
    
    async def generate_lyrics_async(self, genre: str, theme: str, language: str) -> str:
        """
        Asynchroniczne generowanie tekstów
        
        Args:
            genre: Gatunek muzyki
            theme: Temat utworu
            language: Język tekstów
            
        Returns:
            str: Wygenerowane teksty
        """
        prompt = (
            f"Create a {genre} song in {language} about {theme}. "
            f"Write only lyrics, no descriptions. "
            f"Structure: verse, chorus, verse, chorus, bridge, chorus."
        )
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_lyrics_sync, prompt)
    
    def _generate_music_sync(self, lyrics: str, tags: str, duration: int) -> Path:
        """Synchroniczne generowanie muzyki"""
        try:
            print(f"Generating music: duration={duration}s")
            print(f"🔧 CPU Offload enabled: {self.cpu_offload}")
            
            # Monitor VRAM before generation
            if torch.cuda.is_available():
                allocated_before = torch.cuda.memory_allocated() / (1024 ** 3)
                reserved_before = torch.cuda.memory_reserved() / (1024 ** 3)
                print(f"🔍 VRAM before generation - Allocated: {allocated_before:.2f}GB, Reserved: {reserved_before:.2f}GB")
                
                # Try to get real GPU memory usage
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        real_usage = float(result.stdout.strip()) / 1024  # Convert MB to GB
                        print(f"🔍 Real GPU Memory Usage: {real_usage:.2f}GB")
                except:
                    pass
            
            # Load pipeline
            pipeline = self._load_ace_pipeline()
            print(f"🔧 Pipeline CPU Offload status: {pipeline.cpu_offload}")
            
            # Monitor VRAM after pipeline load
            if torch.cuda.is_available():
                allocated_after_load = torch.cuda.memory_allocated() / (1024 ** 3)
                reserved_after_load = torch.cuda.memory_reserved() / (1024 ** 3)
                print(f"🔍 VRAM after pipeline load - Allocated: {allocated_after_load:.2f}GB, Reserved: {reserved_after_load:.2f}GB")
                
                # Try to get real GPU memory usage
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        real_usage = float(result.stdout.strip()) / 1024  # Convert MB to GB
                        print(f"🔍 Real GPU Memory Usage: {real_usage:.2f}GB")
                        
                        # Check if CPU offload is really working
                        if self.cpu_offload and real_usage > 4.0:
                            print(f"⚠️ WARNING: CPU offload enabled but real GPU usage high ({real_usage:.2f}GB)")
                            print(f"🔧 This indicates CPU offload decorators are not working properly")
                except:
                    pass
                    
            # Check if CPU offload is really working with PyTorch memory
            if self.cpu_offload and allocated_after_load > 2.0:
                print(f"⚠️ WARNING: CPU offload enabled but PyTorch VRAM usage high ({allocated_after_load:.2f}GB)")
                print(f"🔧 Models may not be properly moved to CPU")
            
            # Generate music with ACE-Step
            with torch.inference_mode():
                print(f"🔄 Starting music generation with ACE-Step...")
                
                # Monitor VRAM during generation start
                if torch.cuda.is_available():
                    allocated_start = torch.cuda.memory_allocated() / (1024 ** 3)
                    print(f"🔍 VRAM at generation start: {allocated_start:.2f}GB")
                
                results = pipeline(
                    audio_duration=float(duration),
                    prompt=tags,
                    lyrics=lyrics,
                    infer_step=27,
                    guidance_scale=15.0,
                    scheduler_type="euler",
                    cfg_type="apg",
                    omega_scale=10.0,
                    batch_size=1
                )
                
                # Monitor VRAM during generation
                if torch.cuda.is_available():
                    allocated_during = torch.cuda.memory_allocated() / (1024 ** 3)
                    print(f"🔍 VRAM during generation: {allocated_during:.2f}GB")
            
            # Monitor VRAM after generation
            if torch.cuda.is_available():
                allocated_after_gen = torch.cuda.memory_allocated() / (1024 ** 3)
                print(f"🔍 VRAM after generation: {allocated_after_gen:.2f}GB")
            
            audio_path = Path(results[0])
            print(f"Music generated: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"Music generation failed: {e}")
            raise
        finally:
            self._unload_ace_pipeline()
            
            # Monitor VRAM after cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                allocated_final = torch.cuda.memory_allocated() / (1024 ** 3)
                print(f"🔍 VRAM after cleanup: {allocated_final:.2f}GB")
    
    async def generate_music_async(self, lyrics: str, tags: str, duration: int, max_length: int) -> Path:
        """
        Asynchroniczne generowanie muzyki
        
        Args:
            lyrics: Teksty utworu
            tags: Tagi muzyczne
            duration: Żądana długość
            max_length: Maksymalna długość
            
        Returns:
            Path: Ścieżka do wygenerowanego pliku audio
        """
        # Waliduj duration vs max_length
        actual_duration = min(duration, max_length)
        
        loop = asyncio.get_event_loop()
        audio_path = await loop.run_in_executor(
            None, self._generate_music_sync, lyrics, tags, actual_duration
        )
        
        return audio_path
    
    def convert_for_discord(self, audio_path: Path) -> Path:
        """
        Konwertuj audio dla Discord (PCM 48kHz stereo)
        
        Args:
            audio_path: Ścieżka do oryginalnego pliku audio
            
        Returns:
            Path: Ścieżka do skonwertowanego pliku
        """
        try:
            output_path = self.temp_dir / f"discord_{audio_path.stem}.pcm"
            
            # FFmpeg command for Discord-compatible audio
            cmd = [
                "ffmpeg", "-y",  # -y to overwrite
                "-i", str(audio_path),
                "-f", "s16le",  # PCM signed 16-bit little-endian
                "-ar", str(DISCORD_SAMPLE_RATE),  # 48000 Hz
                "-ac", str(DISCORD_CHANNELS),  # 2 channels (stereo)
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            print(f"Audio converted for Discord: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Audio conversion failed: {e}")
            raise
    
    def prepare_upload_file(self, audio_path: Path, format: str = "wav") -> Path:
        """
        Przygotuj plik do uploadu na Discord
        
        Args:
            audio_path: Ścieżka do oryginalnego pliku
            format: Format docelowy (wav, mp3)
            
        Returns:
            Path: Ścieżka do przygotowanego pliku
        """
        try:
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Generate output filename with metadata
            timestamp = int(time.time())
            output_path = self.output_dir / f"discord_upload_{timestamp}.{format}"
            
            if format.lower() == "mp3":
                # Convert to MP3 for smaller file size
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-c:a", "libmp3lame",
                    "-b:a", "192k",  # 192kbps quality
                    str(output_path)
                ]
            else:
                # Keep as WAV or convert to WAV
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-c:a", "pcm_s16le",  # 16-bit PCM
                    str(output_path)
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion error: {result.stderr}")
            
            # Check file size (Discord 8MB limit)
            if output_path.stat().st_size > MAX_FILE_SIZE:
                print(f"Warning: File size ({output_path.stat().st_size / 1024 / 1024:.1f}MB) exceeds Discord limit")
            
            print(f"Upload file prepared: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Upload file preparation failed: {e}")
            raise
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """Wyczyść stare pliki tymczasowe"""
        try:
            current_time = time.time()
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        print(f"Cleaned up old temp file: {file_path}")
        except Exception as e:
            print(f"Temp file cleanup failed: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self._clean_all_memory()
