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
    ELECTRONIC = "electronic"
    HIP_HOP = "hip-hop"
    COUNTRY = "country"
    BLUES = "blues"
    REGGAE = "reggae"
    AMBIENT = "ambient"
    METAL = "metal"
    FUNK = "funk"
    DISCO = "disco"
    PUNK = "punk"

class MusicThemes(Enum):
    """Suggested themes"""
    LOVE = "love"
    PARTY = "party"
    SAD = "sad"
    ENERGETIC = "energetic"
    CHILL = "chill"
    RELAXING = "relaxing"
    MOTIVATIONAL = "motivational"
    ROMANTIC = "romantic"
    NOSTALGIC = "nostalgic"
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"
    CALM = "calm"
    HAPPY = "happy"
    INSTRUMENTAL = "instrumental"

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

# Bot interface language (read from environment, default to Polish)
# Validate against supported languages
_SUPPORTED_INTERFACE_LANGUAGES = ["english", "polish"]
_raw_language = os.getenv("BOT_LANGUAGE", "polish").lower()
BOT_INTERFACE_LANGUAGE = _raw_language if _raw_language in _SUPPORTED_INTERFACE_LANGUAGES else "polish"

# Log warning if invalid language was specified
if _raw_language != BOT_INTERFACE_LANGUAGE:
    print(f"⚠️ Warning: Unsupported language '{_raw_language}', falling back to '{BOT_INTERFACE_LANGUAGE}'")

# Helper functions to get messages in current language
def get_error_message(key: str, **kwargs) -> str:
    """Get error message in current bot interface language
    
    Args:
        key: Message key
        **kwargs: Format arguments (validated to prevent injection)
    
    Returns:
        Formatted error message
    """
    lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
    msg = MESSAGES[lang]["error"].get(key, f"Error: {key}")
    
    # Validate kwargs keys to prevent format string injection
    if kwargs:
        allowed_keys = {"languages", "min", "max", "channel", "title", "setting", "value"}
        validated_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
        return msg.format(**validated_kwargs)
    return msg

def get_success_message(key: str, **kwargs) -> str:
    """Get success message in current bot interface language
    
    Args:
        key: Message key
        **kwargs: Format arguments (validated to prevent injection)
    
    Returns:
        Formatted success message
    """
    lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
    msg = MESSAGES[lang]["success"].get(key, f"Success: {key}")
    
    # Validate kwargs keys to prevent format string injection
    if kwargs:
        allowed_keys = {"languages", "min", "max", "channel", "title", "setting", "value"}
        validated_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
        return msg.format(**validated_kwargs)
    return msg

# Set messages based on configured language
_current_lang = BOT_INTERFACE_LANGUAGE if BOT_INTERFACE_LANGUAGE in MESSAGES else "polish"
ERROR_MESSAGES = MESSAGES[_current_lang]["error"]
SUCCESS_MESSAGES = MESSAGES[_current_lang]["success"]

print(f"🌍 Bot interface language: {_current_lang}")
