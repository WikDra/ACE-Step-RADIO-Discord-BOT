"""
Basic tests dla ACE-Step Discord Radio Bot
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from discord_bot.utils.radio_engine import RadioEngine
from discord_bot.utils.queue_manager import RadioQueue, TrackInfo
from discord_bot.utils.audio_converter import AudioConverter
from discord_bot.config.constants import SupportedLanguages

class TestRadioEngine:
    """Test RadioEngine functions"""
    
    def test_initialization(self):
        """Test RadioEngine initialization"""
        engine = RadioEngine(cpu_offload=True)
        assert engine.cpu_offload == True
        assert engine.device == "cpu"
        assert engine.output_dir.exists()
        assert engine.temp_dir.exists()
    
    @pytest.mark.asyncio
    async def test_lyrics_generation_fallback(self):
        """Test fallback lyrics generation"""
        engine = RadioEngine(cpu_offload=True)
        # Mock LLM to None to force fallback
        engine.llm = None
        
        lyrics = await engine.generate_lyrics_async("pop", "love", "english")
        assert lyrics is not None
        assert len(lyrics) > 0
        assert "[Verse 1]" in lyrics
        assert "[Chorus]" in lyrics
    
    def test_temp_file_cleanup(self):
        """Test temporary file cleanup"""
        engine = RadioEngine(cpu_offload=True)
        
        # Create a test temp file
        test_file = engine.temp_dir / "test_cleanup.txt"
        test_file.write_text("test")
        assert test_file.exists()
        
        # Test cleanup (with max_age_hours=0 to clean immediately)
        engine.cleanup_temp_files(max_age_hours=0)
        
        # File should be removed
        assert not test_file.exists()

class TestRadioQueue:
    """Test queue management"""
    
    def test_initialization(self):
        """Test RadioQueue initialization"""
        queue = RadioQueue()
        assert queue.current_genre == "pop"
        assert queue.current_theme == "love"
        assert queue.current_language == "english"
        assert queue.max_length == 60
        assert queue.auto_queue == True
        assert len(queue.queue) == 0
    
    def test_max_length_validation(self):
        """Test max length validation"""
        queue = RadioQueue()
        
        # Valid values
        assert queue.set_max_length(30) == True
        assert queue.max_length == 30
        assert queue.set_max_length(300) == True
        assert queue.max_length == 300
        
        # Invalid values
        assert queue.set_max_length(20) == False  # Too short
        assert queue.set_max_length(400) == False  # Too long
        assert queue.max_length == 300  # Should stay at previous value
    
    def test_language_validation(self):
        """Test language validation"""
        queue = RadioQueue()
        
        # Valid languages
        assert queue.set_language("english") == True
        assert queue.set_language("polish") == True
        assert queue.set_language("spanish") == True
        
        # Invalid language
        assert queue.set_language("klingon") == False
        assert queue.current_language == "spanish"  # Should stay at previous value
    
    def test_genre_validation(self):
        """Test genre validation"""
        queue = RadioQueue()
        
        # Valid genres
        assert queue.set_genre("pop") == True
        assert queue.set_genre("rock") == True
        assert queue.set_genre("jazz") == True
        
        # Invalid genre
        assert queue.set_genre("unknown_genre") == False
        assert queue.current_genre == "jazz"  # Should stay at previous value
    
    def test_queue_operations(self):
        """Test basic queue operations"""
        queue = RadioQueue()
        
        # Create mock track
        track = TrackInfo(
            path=Path("test.wav"),
            genre="pop",
            theme="love",
            language="english",
            duration=60,
            lyrics="Test lyrics",
            generated_at=pytest.approx(queue)  # datetime.now()
        )
        
        # Test adding track
        queue.add_track(track)
        assert len(queue.queue) == 1
        
        # Test getting next track
        next_track = queue.get_next_track()
        assert next_track == track
        assert queue.current_track == track
        assert len(queue.queue) == 0
        assert len(queue.history) == 0  # Previous current_track was None
        
        # Test skip
        queue.add_track(track)  # Add another track
        skipped = queue.skip_current()
        assert skipped == track
        assert len(queue.history) == 1  # Previous track moved to history
    
    def test_get_track_path(self):
        """Test get_track_path method"""
        queue = RadioQueue()
        
        # No current track
        assert queue.get_track_path() == None
        
        # Set current track
        track = TrackInfo(
            path=Path("current.wav"),
            genre="pop",
            theme="love", 
            language="english",
            duration=60,
            lyrics="Test",
            generated_at=datetime.now()
        )
        queue.current_track = track
        assert queue.get_track_path() == Path("current.wav")
        
        # Add track to queue
        queue_track = TrackInfo(
            path=Path("queued.wav"),
            genre="rock",
            theme="energy",
            language="english", 
            duration=120,
            lyrics="Test",
            generated_at=datetime.now()
        )
        queue.add_track(queue_track)
        
        # Test queue index
        assert queue.get_track_path(0) == Path("queued.wav")
        assert queue.get_track_path(999) == None  # Out of range

class TestAudioConverter:
    """Test audio conversion utilities"""
    
    def test_ffmpeg_check(self):
        """Test FFmpeg availability check"""
        # This will depend on whether FFmpeg is installed
        result = AudioConverter.check_ffmpeg()
        assert isinstance(result, bool)
    
    @patch('subprocess.run')
    def test_get_audio_info(self, mock_subprocess):
        """Test audio info extraction"""
        # Mock ffprobe output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = """
        {
            "streams": [
                {
                    "codec_type": "audio",
                    "duration": "120.5",
                    "sample_rate": "44100",
                    "channels": 2,
                    "codec_name": "pcm_s16le"
                }
            ]
        }
        """
        
        info = AudioConverter.get_audio_info(Path("test.wav"))
        assert info["duration"] == 120.5
        assert info["sample_rate"] == 44100
        assert info["channels"] == 2
        assert info["codec"] == "pcm_s16le"

class TestConstants:
    """Test constants and enums"""
    
    def test_supported_languages(self):
        """Test supported languages enum"""
        # Check that all languages have proper values
        for lang in SupportedLanguages:
            assert len(lang.value) == 2  # (name, flag)
            assert isinstance(lang.value[0], str)  # language name
            assert isinstance(lang.value[1], str)  # flag emoji
    
    def test_language_consistency(self):
        """Test language consistency between components"""
        from discord_bot.utils.queue_manager import RadioQueue
        
        queue = RadioQueue()
        enum_languages = [lang.value[0] for lang in SupportedLanguages]
        queue_languages = queue.SUPPORTED_LANGUAGES
        
        # Check that all enum languages are in queue languages
        for lang in enum_languages:
            assert lang in queue_languages

# Integration tests
class TestIntegration:
    """Integration tests for bot components"""
    
    def test_queue_engine_integration(self):
        """Test integration between queue and engine"""
        queue = RadioQueue()
        engine = RadioEngine(cpu_offload=True)
        
        # Test that queue settings are compatible with engine
        assert queue.set_language("english") == True
        assert queue.set_genre("pop") == True
        assert queue.set_max_length(60) == True
        
        # Test status reporting
        status = queue.get_queue_status()
        assert status["genre"] == "pop"
        assert status["language"] == "english"
        assert status["max_length"] == 60

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
