"""
Audio converter utilities for Discord Bot
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from discord_bot.config.settings import DISCORD_SAMPLE_RATE, DISCORD_CHANNELS, MAX_FILE_SIZE

class AudioConverter:
    """Klasa do konwersji audio dla Discord"""
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Sprawdź czy FFmpeg jest dostępny"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    @staticmethod
    def get_audio_info(audio_path: Path) -> dict:
        """Pobierz informacje o pliku audio"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(audio_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Extract audio stream info
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        return {
                            'duration': float(stream.get('duration', 0)),
                            'sample_rate': int(stream.get('sample_rate', 0)),
                            'channels': int(stream.get('channels', 0)),
                            'codec': stream.get('codec_name', 'unknown')
                        }
            
            return {}
            
        except Exception as e:
            print(f"Failed to get audio info: {e}")
            return {}
    
    @staticmethod
    def convert_to_discord_pcm(input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Konwertuj audio do formatu PCM dla Discord
        
        Args:
            input_path: Ścieżka do pliku wejściowego
            output_path: Ścieżka wyjściowa (opcjonalna)
            
        Returns:
            Path: Ścieżka do skonwertowanego pliku
        """
        if output_path is None:
            output_path = input_path.parent / f"discord_{input_path.stem}.pcm"
        
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-i', str(input_path),
            '-f', 's16le',  # PCM signed 16-bit little-endian
            '-ar', str(DISCORD_SAMPLE_RATE),  # 48000 Hz
            '-ac', str(DISCORD_CHANNELS),  # 2 channels
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")
        
        return output_path
    
    @staticmethod
    def convert_for_upload(input_path: Path, format: str = "mp3", 
                          max_size_mb: float = 8.0) -> Path:
        """
        Konwertuj audio do uploadu na Discord
        
        Args:
            input_path: Ścieżka do pliku wejściowego
            format: Format docelowy (mp3, wav, ogg)
            max_size_mb: Maksymalny rozmiar w MB
            
        Returns:
            Path: Ścieżka do skonwertowanego pliku
        """
        output_path = input_path.parent / f"upload_{input_path.stem}.{format}"
        
        # Determine conversion settings based on format
        if format.lower() == "mp3":
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c:a', 'libmp3lame',
                '-b:a', '192k',  # 192 kbps
                '-ar', '44100',  # Standard sample rate
                str(output_path)
            ]
        elif format.lower() == "ogg":
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c:a', 'libvorbis',
                '-b:a', '192k',
                '-ar', '44100',
                str(output_path)
            ]
        else:  # wav or other
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-c:a', 'pcm_s16le',  # 16-bit PCM
                '-ar', '44100',
                str(output_path)
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")
        
        # Check file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            # Try to reduce quality
            if format.lower() == "mp3":
                # Try with lower bitrate
                lower_bitrate_path = input_path.parent / f"upload_compressed_{input_path.stem}.{format}"
                cmd = [
                    'ffmpeg', '-y',
                    '-i', str(input_path),
                    '-c:a', 'libmp3lame',
                    '-b:a', '128k',  # Lower bitrate
                    '-ar', '44100',
                    str(lower_bitrate_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # Remove original and use compressed version
                    output_path.unlink()
                    output_path = lower_bitrate_path
                    file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print(f"Converted for upload: {output_path} ({file_size_mb:.1f}MB)")
        return output_path
    
    @staticmethod
    def trim_audio(input_path: Path, start_seconds: float = 0, 
                   duration_seconds: Optional[float] = None) -> Path:
        """
        Przytnij audio do określonej długości
        
        Args:
            input_path: Ścieżka do pliku wejściowego
            start_seconds: Początek w sekundach
            duration_seconds: Długość w sekundach (None = do końca)
            
        Returns:
            Path: Ścieżka do przyciętego pliku
        """
        output_path = input_path.parent / f"trimmed_{input_path.stem}{input_path.suffix}"
        
        cmd = ['ffmpeg', '-y', '-i', str(input_path)]
        
        if start_seconds > 0:
            cmd.extend(['-ss', str(start_seconds)])
        
        if duration_seconds is not None:
            cmd.extend(['-t', str(duration_seconds)])
        
        cmd.extend(['-c', 'copy', str(output_path)])  # Copy without re-encoding
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg trim failed: {result.stderr}")
        
        return output_path
    
    @staticmethod
    def add_fade(input_path: Path, fade_in: float = 1.0, fade_out: float = 3.0) -> Path:
        """
        Dodaj fade in/out do audio
        
        Args:
            input_path: Ścieżka do pliku wejściowego
            fade_in: Długość fade in w sekundach
            fade_out: Długość fade out w sekundach
            
        Returns:
            Path: Ścieżka do pliku z fade
        """
        output_path = input_path.parent / f"faded_{input_path.stem}{input_path.suffix}"
        
        # Get audio duration first
        info = AudioConverter.get_audio_info(input_path)
        duration = info.get('duration', 0)
        
        if duration == 0:
            raise Exception("Could not determine audio duration")
        
        # Create fade filter
        fade_out_start = max(0, duration - fade_out)
        filter_str = f"afade=t=in:ss=0:d={fade_in},afade=t=out:st={fade_out_start}:d={fade_out}"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-af', filter_str,
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg fade failed: {result.stderr}")
        
        return output_path
