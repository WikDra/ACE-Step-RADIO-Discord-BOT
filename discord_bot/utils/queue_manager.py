"""
QueueManager - Zarządzanie kolejką utworów Discord Bot
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

# Local imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from discord_bot.config.settings import *
from discord_bot.config.constants import SupportedLanguages

@dataclass
class TrackInfo:
    """Struktura informacji o utworze"""
    path: Path
    genre: str
    theme: str
    language: str
    duration: int
    lyrics: str
    generated_at: datetime
    title: str = ""
    artist: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "path": str(self.path),
            "genre": self.genre,
            "theme": self.theme,
            "language": self.language,
            "duration": self.duration,
            "lyrics": self.lyrics,
            "generated_at": self.generated_at.isoformat(),
            "title": self.title,
            "artist": self.artist
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TrackInfo':
        """Create from dictionary"""
        return cls(
            path=Path(data["path"]),
            genre=data["genre"],
            theme=data["theme"],
            language=data["language"],
            duration=data["duration"],
            lyrics=data["lyrics"],
            generated_at=datetime.fromisoformat(data["generated_at"]),
            title=data.get("title", ""),
            artist=data.get("artist", "")
        )

class RadioQueue:
    """Zarządzanie kolejką radio"""
    
    # Obsługiwane języki z ACE-Step
    SUPPORTED_LANGUAGES = [lang.value[0] for lang in SupportedLanguages]
    
    def __init__(self):
        """Inicjalizacja kolejki z domyślnymi ustawieniami"""
        
        # Ustawienia domyślne z radio_gradio.py
        self.current_genre = DEFAULT_GENRE
        self.current_theme = DEFAULT_THEME
        self.current_language = DEFAULT_LANGUAGE
        self.max_length = 60  # NOWA FUNKCJA - max długość utworów
        self.buffer_size = BUFFER_SIZE
        self.auto_queue = True
        
        # Struktury danych
        self.queue: List[TrackInfo] = []
        self.history: List[TrackInfo] = []
        self.current_track: Optional[TrackInfo] = None
        
        print(f"RadioQueue initialized - Genre: {self.current_genre}, Theme: {self.current_theme}, Language: {self.current_language}")
    
    def set_max_length(self, seconds: int) -> bool:
        """
        Walidacja i ustawienie maksymalnej długości utworów
        
        Args:
            seconds: Maksymalna długość w sekundach
            
        Returns:
            bool: True jeśli ustawiono pomyślnie
        """
        if MAX_LENGTH_MIN <= seconds <= MAX_LENGTH_MAX:
            self.max_length = seconds
            print(f"Max length set to: {seconds}s")
            return True
        else:
            print(f"Invalid max length: {seconds}s (must be {MAX_LENGTH_MIN}-{MAX_LENGTH_MAX}s)")
            return False
    
    def set_genre(self, genre: str) -> bool:
        """
        Walidacja i ustawienie gatunku
        
        Args:
            genre: Gatunek muzyki
            
        Returns:
            bool: True jeśli ustawiono pomyślnie
        """
        # Lista gatunków z radio_gradio.py
        valid_genres = [
            "pop", "rock", "hip hop", "electronic", "lofi", "jazz", 
            "classical", "ambient", "country", "metal", "death metal", 
            "doom metal", "reggae", "dub", "blues", "delta blues", 
            "funk", "disco", "punk"
        ]
        
        if genre.lower() in valid_genres:
            self.current_genre = genre.lower()
            print(f"Genre set to: {self.current_genre}")
            return True
        else:
            print(f"Invalid genre: {genre}")
            return False
    
    def set_theme(self, theme: str) -> bool:
        """
        Ustawienie tematu (bez walidacji - dowolny tekst)
        
        Args:
            theme: Temat utworu
            
        Returns:
            bool: Zawsze True
        """
        self.current_theme = theme
        print(f"Theme set to: {self.current_theme}")
        return True
    
    def set_language(self, language: str) -> bool:
        """
        Walidacja i ustawienie języka
        
        Args:
            language: Język tekstów
            
        Returns:
            bool: True jeśli ustawiono pomyślnie
        """
        if language.lower() in self.SUPPORTED_LANGUAGES:
            self.current_language = language.lower()
            print(f"Language set to: {self.current_language}")
            return True
        else:
            print(f"Invalid language: {language}. Supported: {self.SUPPORTED_LANGUAGES}")
            return False
    
    def set_auto_queue(self, enabled: bool) -> None:
        """
        Włącz/wyłącz automatyczne dodawanie utworów
        
        Args:
            enabled: Czy włączyć auto-queue
        """
        self.auto_queue = enabled
        print(f"Auto-queue set to: {enabled}")
    
    def add_track(self, track: TrackInfo) -> None:
        """
        Dodaj utwór do kolejki
        
        Args:
            track: Informacje o utworze
        """
        self.queue.append(track)
        print(f"Track added to queue: {track.title or track.theme} ({len(self.queue)} total)")
    
    def get_next_track(self) -> Optional[TrackInfo]:
        """
        Pobierz następny utwór z kolejki
        
        Returns:
            TrackInfo: Następny utwór lub None jeśli kolejka pusta
        """
        if self.queue:
            track = self.queue.pop(0)
            
            # Przenieś current track do historii
            if self.current_track:
                self.history.append(self.current_track)
                
                # Ogranicz historię
                if len(self.history) > 50:  # Max 50 utworów w historii
                    self.history.pop(0)
            
            self.current_track = track
            print(f"Next track: {track.title or track.theme}")
            return track
        
        return None
    
    def skip_current(self) -> Optional[TrackInfo]:
        """
        Pomiń obecny utwór i pobierz następny
        
        Returns:
            TrackInfo: Następny utwór lub None
        """
        print("Skipping current track")
        return self.get_next_track()
    
    def clear_queue(self) -> None:
        """Wyczyść kolejkę"""
        self.queue.clear()
        print("Queue cleared")
    
    def clear_history(self) -> None:
        """Wyczyść historię"""
        self.history.clear()
        print("History cleared")
    
    async def ensure_buffer_full(self, radio_engine) -> None:
        """
        Auto-filling buffer jak w radio_gradio.py
        
        Args:
            radio_engine: Instancja RadioEngine do generowania utworów
        """
        if not self.auto_queue:
            return
        
        while len(self.queue) < self.buffer_size:
            try:
                print(f"Buffer low ({len(self.queue)}/{self.buffer_size}), generating new track...")
                
                # Generate lyrics
                lyrics = await radio_engine.generate_lyrics_async(
                    self.current_genre, 
                    self.current_theme, 
                    self.current_language
                )
                
                # Generate music
                tags = f"{self.current_genre} song about {self.current_theme}"
                audio_path = await radio_engine.generate_music_async(
                    lyrics, tags, 60, self.max_length  # Default 60s, limited by max_length
                )
                
                # Create track info
                track = TrackInfo(
                    path=audio_path,
                    genre=self.current_genre,
                    theme=self.current_theme,
                    language=self.current_language,
                    duration=min(60, self.max_length),
                    lyrics=lyrics,
                    generated_at=datetime.now(),
                    title=f"{self.current_theme.title()} Song",
                    artist="AI Radio"
                )
                
                self.add_track(track)
                
            except Exception as e:
                print(f"Failed to generate track for buffer: {e}")
                break  # Stop trying if generation fails
    
    def get_queue_status(self) -> Dict:
        """
        Zwróć status kolejki
        
        Returns:
            dict: Status kolejki
        """
        return {
            "genre": self.current_genre,
            "theme": self.current_theme,
            "language": self.current_language,
            "max_length": self.max_length,
            "auto_queue": self.auto_queue,
            "queue_length": len(self.queue),
            "history_length": len(self.history),
            "current_track": self.current_track.title if self.current_track else None
        }
    
    def get_track_path(self, track_index: Optional[int] = None) -> Optional[Path]:
        """
        Pobierz ścieżkę pliku z kolejki
        
        Args:
            track_index: Indeks utworu w kolejce (None = current track)
            
        Returns:
            Path: Ścieżka do pliku lub None
        """
        if track_index is None:
            # Return current track path
            return self.current_track.path if self.current_track else None
        
        # Return specific track from queue
        if 0 <= track_index < len(self.queue):
            return self.queue[track_index].path
        
        return None
    
    def get_queue_list(self) -> List[Dict]:
        """
        Pobierz listę utworów w kolejce
        
        Returns:
            List[Dict]: Lista informacji o utworach
        """
        return [
            {
                "index": i,
                "title": track.title or f"{track.theme} ({track.genre})",
                "genre": track.genre,
                "theme": track.theme,
                "language": track.language,
                "duration": f"{track.duration}s"
            }
            for i, track in enumerate(self.queue)
        ]
    
    def get_history_list(self) -> List[Dict]:
        """
        Pobierz listę utworów z historii
        
        Returns:
            List[Dict]: Lista utworów z historii
        """
        return [
            {
                "title": track.title or f"{track.theme} ({track.genre})",
                "genre": track.genre,
                "theme": track.theme,
                "language": track.language,
                "duration": f"{track.duration}s",
                "generated_at": track.generated_at.strftime("%H:%M:%S")
            }
            for track in reversed(self.history[-10:])  # Last 10 tracks, newest first
        ]
    
    def save_state(self, file_path: Path) -> None:
        """
        Zapisz stan kolejki do pliku
        
        Args:
            file_path: Ścieżka do pliku zapisu
        """
        try:
            state = {
                "settings": {
                    "current_genre": self.current_genre,
                    "current_theme": self.current_theme,
                    "current_language": self.current_language,
                    "max_length": self.max_length,
                    "auto_queue": self.auto_queue
                },
                "queue": [track.to_dict() for track in self.queue],
                "history": [track.to_dict() for track in self.history[-20:]],  # Save last 20
                "current_track": self.current_track.to_dict() if self.current_track else None,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print(f"Queue state saved to: {file_path}")
            
        except Exception as e:
            print(f"Failed to save queue state: {e}")
    
    def load_state(self, file_path: Path) -> bool:
        """
        Załaduj stan kolejki z pliku
        
        Args:
            file_path: Ścieżka do pliku
            
        Returns:
            bool: True jeśli załadowano pomyślnie
        """
        try:
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Load settings
            settings = state.get("settings", {})
            self.current_genre = settings.get("current_genre", DEFAULT_GENRE)
            self.current_theme = settings.get("current_theme", DEFAULT_THEME)
            self.current_language = settings.get("current_language", DEFAULT_LANGUAGE)
            self.max_length = settings.get("max_length", 60)
            self.auto_queue = settings.get("auto_queue", True)
            
            # Load queue (only if paths still exist)
            self.queue = []
            for track_data in state.get("queue", []):
                try:
                    track = TrackInfo.from_dict(track_data)
                    if track.path.exists():
                        self.queue.append(track)
                except Exception:
                    pass  # Skip invalid tracks
            
            # Load history
            self.history = []
            for track_data in state.get("history", []):
                try:
                    track = TrackInfo.from_dict(track_data)
                    self.history.append(track)
                except Exception:
                    pass  # Skip invalid tracks
            
            # Load current track
            current_data = state.get("current_track")
            if current_data:
                try:
                    self.current_track = TrackInfo.from_dict(current_data)
                    if not self.current_track.path.exists():
                        self.current_track = None
                except Exception:
                    self.current_track = None
            
            print(f"Queue state loaded from: {file_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load queue state: {e}")
            return False
