"""
Constants and enums for ACE-Step Discord Bot
"""
from enum import Enum
import os

class SupportedLanguages(Enum):
    """From ACE-Step documentation - lyrics languages"""
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
    """Suggested genres for ACE-Step"""
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
    """Suggested themes"""
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

# Bot interface language (read from environment, default to Polish)
BOT_INTERFACE_LANGUAGE = os.getenv("BOT_LANGUAGE", "polish").lower()

# Multi-language messages for bot interface
MESSAGES = {
    "english": {
        "error": {
            "not_in_voice": "❌ You must be in a voice channel!",
            "bot_not_connected": "❌ Bot is not connected to a voice channel!",
            "invalid_language": "❌ Unsupported language. Available: {languages}",
            "invalid_duration": "❌ Duration must be between {min} and {max} seconds.",
            "generation_failed": "❌ Track generation failed. Please try again.",
            "no_permission": "❌ No permission to join the voice channel!",
            "file_too_large": "❌ File is too large for upload (max 8MB)!",
            "no_track": "❌ No track to upload!",
        },
        "success": {
            "joined": "🎵 Joined **{channel}**!",
            "playing": "▶️ Now playing: **{title}**",
            "skipped": "⏭️ Track skipped",
            "stopped": "⏹️ Radio stopped",
            "setting_updated": "✅ {setting} changed to **{value}**",
            "uploaded": "📤 Track file uploaded! (format: MP3)",
        }
    },
    "polish": {
        "error": {
            "not_in_voice": "❌ Musisz być w kanale głosowym!",
            "bot_not_connected": "❌ Bot nie jest połączony z kanałem głosowym!",
            "invalid_language": "❌ Nieobsługiwany język. Dostępne: {languages}",
            "invalid_duration": "❌ Długość musi być między {min} a {max} sekund.",
            "generation_failed": "❌ Błąd generowania utworu. Spróbuj ponownie.",
            "no_permission": "❌ Brak uprawnień do dołączenia do kanału głosowego!",
            "file_too_large": "❌ Plik jest za duży do uploadu (max 8MB)!",
            "no_track": "❌ Brak utworu do uploadu!",
        },
        "success": {
            "joined": "🎵 Dołączyłem do **{channel}**!",
            "playing": "▶️ Teraz gra: **{title}**",
            "skipped": "⏭️ Utwór pominięty",
            "stopped": "⏹️ Radio zatrzymane",
            "setting_updated": "✅ {setting} zmienione na **{value}**",
            "uploaded": "📤 Plik z utworem wrzucony! (format: MP3)",
        }
    }
}

# Helper functions to get messages in current language
def get_error_message(key: str, **kwargs) -> str:
    """Get error message in current bot interface language"""
    lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
    msg = MESSAGES[lang]["error"].get(key, f"Error: {key}")
    return msg.format(**kwargs) if kwargs else msg

def get_success_message(key: str, **kwargs) -> str:
    """Get success message in current bot interface language"""
    lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
    msg = MESSAGES[lang]["success"].get(key, f"Success: {key}")
    return msg.format(**kwargs) if kwargs else msg

# Set messages based on configured language
_current_lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
ERROR_MESSAGES = MESSAGES[_current_lang]["error"]
SUCCESS_MESSAGES = MESSAGES[_current_lang]["success"]

print(f"🌍 Bot interface language: {_current_lang}")
