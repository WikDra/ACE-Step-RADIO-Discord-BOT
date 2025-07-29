"""
Stałe i enums dla ACE-Step Discord Bot
"""
from enum import Enum

class SupportedLanguages(Enum):
    """Z ACE-Step documentation"""
    ENGLISH = ("english", "🇺🇸")
    POLISH = ("polish", "🇵🇱") 
    SPANISH = ("spanish", "🇪🇸")
    FRENCH = ("french", "🇫🇷")
    GERMAN = ("german", "🇩🇪")
    ITALIAN = ("italian", "🇮🇹")
    PORTUGUESE = ("portuguese", "🇵🇹")
    RUSSIAN = ("russian", "🇷🇺")
    CHINESE = ("chinese", "🇨🇳")
    JAPANESE = ("japanese", "🇯🇵")
    KOREAN = ("korean", "🇰🇷")

class MusicGenres(Enum):
    """Sugerowane gatunki dla ACE-Step"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    EDM = "edm"
    HIP_HOP = "hip-hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    AMBIENT = "ambient"

class MusicThemes(Enum):
    """Sugerowane tematy"""
    LOVE = "love"
    PARTY = "party"
    SAD = "sad"
    ENERGETIC = "energetic"
    CHILL = "chill"
    MOTIVATIONAL = "motivational"
    ROMANTIC = "romantic"
    NOSTALGIC = "nostalgic"
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"

# Error messages
ERROR_MESSAGES = {
    "not_in_voice": "❌ Musisz być w kanale głosowym!",
    "bot_not_connected": "❌ Bot nie jest połączony z kanałem głosowym!",
    "invalid_language": "❌ Nieobsługiwany język. Dostępne: {languages}",
    "invalid_duration": "❌ Długość musi być między {min} a {max} sekund.",
    "generation_failed": "❌ Błąd generowania utworu. Spróbuj ponownie.",
    "no_permission": "❌ Brak uprawnień do dołączenia do kanału głosowego!",
    "file_too_large": "❌ Plik jest za duży do uploadu (max 8MB)!",
    "no_track": "❌ Brak utworu do uploadu!",
}

# Success messages
SUCCESS_MESSAGES = {
    "joined": "🎵 Dołączyłem do **{channel}**!",
    "playing": "▶️ Teraz gra: **{title}**",
    "skipped": "⏭️ Utwór pominięty",
    "stopped": "⏹️ Radio zatrzymane",
    "setting_updated": "✅ {setting} zmienione na **{value}**",
    "uploaded": "📤 Plik z utworem wrzucony! (format: MP3)",
}
