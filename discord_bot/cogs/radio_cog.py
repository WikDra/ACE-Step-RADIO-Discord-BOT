"""
Radio Cog - Główne komendy Discord dla ACE-Step Radio Bot
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

# Local imports
from ..utils.radio_engine import RadioEngine
from ..utils.queue_manager import RadioQueue, TrackInfo
from ..utils.audio_converter import AudioConverter
from ..utils.metrics import get_metrics
from ..config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES, SupportedLanguages, MusicGenres, MusicThemes
from ..config.settings import *

class RadioCog(commands.Cog):
    """Główny cog z komendami Discord Radio"""
    
    def __init__(self, bot):
        """Inicjalizacja cog"""
        self.bot = bot
        self.radio_engine = RadioEngine()
        self.voice_clients = {}  # guild_id: discord.VoiceClient
        self.queues = {}        # guild_id: RadioQueue  
        self.playing_tasks = {} # guild_id: asyncio.Task
        
        # Load presets
        presets_path = Path(__file__).parent.parent / "data" / "presets.json"
        try:
            with open(presets_path, 'r', encoding='utf-8') as f:
                self.presets = json.load(f)
        except Exception as e:
            print(f"Failed to load presets: {e}")
            self.presets = {}
        
        print("RadioCog initialized")
    
    def get_queue(self, guild_id: int) -> RadioQueue:
        """Pobierz lub stwórz kolejkę dla serwera"""
        if guild_id not in self.queues:
            self.queues[guild_id] = RadioQueue()
        return self.queues[guild_id]
    
    def create_embed(self, title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
        """Stwórz standardowy embed"""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="ACE-Step Radio Bot")
        return embed
    
    def create_error_embed(self, message: str) -> discord.Embed:
        """Stwórz embed z błędem"""
        return self.create_embed("❌ Błąd", message, discord.Color.red())
    
    def create_success_embed(self, message: str) -> discord.Embed:
        """Stwórz embed z sukcesem"""
        return self.create_embed("✅ Sukces", message, discord.Color.green())

    # ==================== PODSTAWOWE KOMENDY ====================
    
    @app_commands.command(name="radio_join", description="Dołącz do kanału głosowego")
    async def radio_join(self, interaction: discord.Interaction):
        """Dołącz do kanału głosowego"""
        # Track command
        metrics = get_metrics()
        if metrics:
            metrics.record_command_execution("radio_join")
        
        # Sprawdź czy user jest w voice channel
        if not interaction.user.voice:
            embed = self.create_error_embed(ERROR_MESSAGES["not_in_voice"])
            await interaction.response.send_message(embed=embed)
            return
        
        channel = interaction.user.voice.channel
        
        # Sprawdź czy bot już połączony
        if interaction.guild.id in self.voice_clients:
            # Przenieś do nowego kanału
            await self.voice_clients[interaction.guild.id].move_to(channel)
        else:
            # Połącz do kanału
            try:
                voice_client = await channel.connect()
                self.voice_clients[interaction.guild.id] = voice_client
            except Exception as e:
                embed = self.create_error_embed(f"Nie mogę dołączyć do kanału: {str(e)}")
                await interaction.response.send_message(embed=embed)
                return
        
        embed = self.create_success_embed(SUCCESS_MESSAGES["joined"].format(channel=channel.name))
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_play", description="Zagraj utwór z podanymi parametrami")
    @app_commands.describe(
        genre="Gatunek muzyki",
        theme="Temat utworu", 
        language="Język tekstów",
        duration="Długość utworu w sekundach"
    )
    async def radio_play(self, interaction: discord.Interaction,
                        genre: str = DEFAULT_GENRE,
                        theme: str = DEFAULT_THEME, 
                        language: str = DEFAULT_LANGUAGE,
                        duration: int = DEFAULT_DURATION):
        """Główna komenda odtwarzania"""
        
        # Track command and parameters
        metrics = get_metrics()
        if metrics:
            metrics.record_command_execution("radio_play")
        
        # Sprawdź czy bot w voice channel
        if interaction.guild.id not in self.voice_clients:
            embed = self.create_error_embed(ERROR_MESSAGES["bot_not_connected"])
            await interaction.response.send_message(embed=embed)
            return
        
        voice_client = self.voice_clients[interaction.guild.id]
        if not voice_client.is_connected():
            embed = self.create_error_embed(ERROR_MESSAGES["bot_not_connected"])
            await interaction.response.send_message(embed=embed)
            return
        
        # Defer response - generowanie może trwać długo
        await interaction.response.defer()
        
        try:
            # Get/create RadioQueue dla guild
            queue = self.get_queue(interaction.guild.id)
            
            # Update queue settings jeśli podane
            queue.set_genre(genre)
            queue.set_theme(theme)
            queue.set_language(language)
            
            # Validate duration vs max_length
            actual_duration = min(duration, queue.max_length)
            if actual_duration != duration:
                await interaction.followup.send(
                    f"⚠️ Długość skrócona z {duration}s do {actual_duration}s (max: {queue.max_length}s)"
                )
            
            # Generate track
            status_embed = self.create_embed("🎵 Generowanie", "Tworzę utwór, to może potrwać chwilę...")
            await interaction.followup.send(embed=status_embed)
            
            start_time = time.time()
            
            # Generate lyrics
            lyrics = await self.radio_engine.generate_lyrics_async(genre, theme, language)
            
            # Generate music
            tags = f"{genre} song about {theme}"
            audio_path = await self.radio_engine.generate_music_async(
                lyrics, tags, actual_duration, queue.max_length
            )
            
            generation_time = time.time() - start_time
            
            # Track generation metrics
            if metrics:
                metrics.record_song_generation(genre, language, generation_time)
            
            # Convert for Discord
            discord_audio_path = self.radio_engine.convert_for_discord(audio_path)
            
            # Stop current playback if any
            if voice_client.is_playing():
                voice_client.stop()
            
            # Play audio
            source = discord.FFmpegPCMAudio(str(discord_audio_path))
            voice_client.play(source)
            
            # Create track info
            track = TrackInfo(
                path=audio_path,
                genre=genre,
                theme=theme,
                language=language,
                duration=actual_duration,
                lyrics=lyrics,
                generated_at=datetime.now(),
                title=f"{theme.title()}",
                artist="AI Radio"
            )
            
            # Update current track
            queue.current_track = track
            
            # Create success embed with track info
            embed = self.create_embed(
                "🎵 Teraz gra",
                f"**{track.title}**\n"
                f"Gatunek: {genre}\n"
                f"Temat: {theme}\n"
                f"Język: {language}\n"
                f"Długość: {actual_duration}s",
                discord.Color.green()
            )
            
            await interaction.edit_original_response(embed=embed)
            
            # Start auto-queue task jeśli włączone
            if queue.auto_queue and interaction.guild.id not in self.playing_tasks:
                task = asyncio.create_task(self._auto_queue_task(interaction.guild.id))
                self.playing_tasks[interaction.guild.id] = task
            
        except Exception as e:
            # Track error
            if metrics:
                metrics.record_error("radio_play_generation")
            
            embed = self.create_error_embed(f"Błąd generowania: {str(e)}")
            await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="radio_skip", description="Pomiń obecny utwór")
    async def radio_skip(self, interaction: discord.Interaction):
        """Skip current track"""
        if interaction.guild.id not in self.voice_clients:
            embed = self.create_error_embed(ERROR_MESSAGES["bot_not_connected"])
            await interaction.response.send_message(embed=embed)
            return
        
        voice_client = self.voice_clients[interaction.guild.id]
        
        if voice_client.is_playing():
            voice_client.stop()
            embed = self.create_success_embed(SUCCESS_MESSAGES["skipped"])
        else:
            embed = self.create_error_embed("Nic nie gra")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_stop", description="Zatrzymaj radio i opuść kanał")
    async def radio_stop(self, interaction: discord.Interaction):
        """Stop and cleanup"""
        guild_id = interaction.guild.id
        
        # Stop playback
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            if voice_client.is_playing():
                voice_client.stop()
            
            # Disconnect
            await voice_client.disconnect()
            del self.voice_clients[guild_id]
        
        # Cancel auto-queue task
        if guild_id in self.playing_tasks:
            self.playing_tasks[guild_id].cancel()
            del self.playing_tasks[guild_id]
        
        # Clear queue
        if guild_id in self.queues:
            self.queues[guild_id].clear_queue()
        
        embed = self.create_success_embed(SUCCESS_MESSAGES["stopped"])
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_upload", description="Wrzuć plik z obecnym utworem na kanał")
    @app_commands.describe(track_index="Indeks utworu w kolejce (opcjonalny)")
    async def radio_upload(self, interaction: discord.Interaction, track_index: Optional[int] = None):
        """Wrzuć plik z piosenką na kanał"""
        
        # Track command
        metrics = get_metrics()
        if metrics:
            metrics.record_command_execution("radio_upload")
        
        queue = self.get_queue(interaction.guild.id)
        
        # Pobierz ścieżkę pliku
        audio_path = queue.get_track_path(track_index)
        
        if audio_path is None:
            embed = self.create_error_embed(ERROR_MESSAGES["no_track"])
            await interaction.response.send_message(embed=embed)
            return
        
        await interaction.response.defer()
        
        try:
            # Przygotuj plik do uploadu
            upload_path = self.radio_engine.prepare_upload_file(audio_path, format="mp3")
            
            # Sprawdź rozmiar pliku
            file_size = upload_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                embed = self.create_error_embed(ERROR_MESSAGES["file_too_large"])
                await interaction.followup.send(embed=embed)
                return
            
            # Upload file
            file = discord.File(str(upload_path), filename=f"ace_radio_{upload_path.name}")
            
            # Get track info for embed
            track = queue.current_track if track_index is None else queue.queue[track_index]
            track_info = f"Gatunek: {track.genre}, Temat: {track.theme}" if track else ""
            
            embed = self.create_success_embed(
                f"📤 {SUCCESS_MESSAGES['uploaded']}\n{track_info}"
            )
            
            await interaction.followup.send(embed=embed, file=file)
            
            # Track successful upload
            if metrics:
                metrics.record_upload()
            
            # Opcjonalnie usuń plik po uploadzie
            try:
                upload_path.unlink()
            except Exception:
                pass
            
        except Exception as e:
            # Track upload error
            if metrics:
                metrics.record_error("radio_upload")
            
            embed = self.create_error_embed(f"Błąd uploadu: {str(e)}")
            await interaction.followup.send(embed=embed)

    # ==================== USTAWIENIA ====================
    
    @app_commands.command(name="radio_genre", description="Ustaw gatunek muzyki")
    @app_commands.describe(genre="Nowy gatunek muzyki")
    async def radio_genre(self, interaction: discord.Interaction, genre: str):
        """Ustaw gatunek"""
        queue = self.get_queue(interaction.guild.id)
        
        if queue.set_genre(genre):
            embed = self.create_success_embed(
                SUCCESS_MESSAGES["setting_updated"].format(setting="Gatunek", value=genre)
            )
        else:
            valid_genres = ", ".join(["pop", "rock", "jazz", "edm", "classical", "hip-hop"])
            embed = self.create_error_embed(f"Nieprawidłowy gatunek. Dostępne: {valid_genres}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_theme", description="Ustaw temat utworów")
    @app_commands.describe(theme="Nowy temat utworów")
    async def radio_theme(self, interaction: discord.Interaction, theme: str):
        """Ustaw temat"""
        queue = self.get_queue(interaction.guild.id)
        queue.set_theme(theme)
        
        embed = self.create_success_embed(
            SUCCESS_MESSAGES["setting_updated"].format(setting="Temat", value=theme)
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_language", description="Ustaw język tekstów")
    @app_commands.describe(language="Język dla tekstów utworów")
    async def radio_language(self, interaction: discord.Interaction, language: str):
        """Ustaw język"""
        queue = self.get_queue(interaction.guild.id)
        
        if queue.set_language(language):
            embed = self.create_success_embed(
                SUCCESS_MESSAGES["setting_updated"].format(setting="Język", value=language)
            )
        else:
            valid_languages = ", ".join(queue.SUPPORTED_LANGUAGES)
            embed = self.create_error_embed(
                ERROR_MESSAGES["invalid_language"].format(languages=valid_languages)
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_maxlength", description="Ustaw maksymalną długość utworów")
    @app_commands.describe(seconds="Maksymalna długość w sekundach (30-300)")
    async def radio_maxlength(self, interaction: discord.Interaction, seconds: int):
        """Ustaw maksymalną długość"""
        queue = self.get_queue(interaction.guild.id)
        
        if queue.set_max_length(seconds):
            embed = self.create_success_embed(
                SUCCESS_MESSAGES["setting_updated"].format(setting="Maks. długość", value=f"{seconds}s")
            )
        else:
            embed = self.create_error_embed(
                ERROR_MESSAGES["invalid_duration"].format(min=MAX_LENGTH_MIN, max=MAX_LENGTH_MAX)
            )
        
        await interaction.response.send_message(embed=embed)

    # ==================== KOLEJKA ====================
    
    @app_commands.command(name="radio_auto", description="Włącz/wyłącz automatyczne dodawanie utworów")
    @app_commands.describe(enabled="Czy włączyć auto-queue")
    async def radio_auto(self, interaction: discord.Interaction, enabled: bool):
        """Toggle auto-queue"""
        queue = self.get_queue(interaction.guild.id)
        queue.set_auto_queue(enabled)
        
        status = "włączone" if enabled else "wyłączone"
        embed = self.create_success_embed(f"Auto-queue {status}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_queue_list", description="Pokaż kolejkę utworów")
    async def radio_queue_list(self, interaction: discord.Interaction):
        """Pokaż kolejkę"""
        queue = self.get_queue(interaction.guild.id)
        queue_list = queue.get_queue_list()
        
        if not queue_list:
            embed = self.create_embed("📋 Kolejka", "Kolejka jest pusta")
        else:
            description = "\n".join([
                f"{i+1}. {track['title']} ({track['duration']})"
                for i, track in enumerate(queue_list[:10])  # Show max 10
            ])
            
            if len(queue_list) > 10:
                description += f"\n... i {len(queue_list) - 10} więcej"
            
            embed = self.create_embed("📋 Kolejka", description)
        
        await interaction.response.send_message(embed=embed)

    # ==================== INFO ====================
    
    @app_commands.command(name="radio_settings", description="Pokaż obecne ustawienia")
    async def radio_settings(self, interaction: discord.Interaction):
        """Pokaż ustawienia"""
        queue = self.get_queue(interaction.guild.id)
        status = queue.get_queue_status()
        
        embed = self.create_embed(
            "⚙️ Ustawienia Radio",
            f"**Gatunek:** {status['genre']}\n"
            f"**Temat:** {status['theme']}\n"
            f"**Język:** {status['language']}\n"
            f"**Maks. długość:** {status['max_length']}s\n"
            f"**Auto-queue:** {'Tak' if status['auto_queue'] else 'Nie'}\n"
            f"**Utworów w kolejce:** {status['queue_length']}\n"
            f"**Obecny utwór:** {status['current_track'] or 'Brak'}"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_nowplaying", description="Co teraz gra")
    async def radio_nowplaying(self, interaction: discord.Interaction):
        """Co gra teraz"""
        queue = self.get_queue(interaction.guild.id)
        
        if queue.current_track:
            track = queue.current_track
            embed = self.create_embed(
                "🎵 Teraz gra",
                f"**{track.title}**\n"
                f"Gatunek: {track.genre}\n"
                f"Temat: {track.theme}\n"
                f"Język: {track.language}\n"
                f"Długość: {track.duration}s\n"
                f"Wygenerowano: {track.generated_at.strftime('%H:%M:%S')}"
            )
        else:
            embed = self.create_embed("🎵 Teraz gra", "Nic nie gra")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_preset", description="Użyj gotowego presetu")
    @app_commands.describe(preset_name="Nazwa presetu")
    async def radio_preset(self, interaction: discord.Interaction, preset_name: str):
        """Użyj presetu"""
        if preset_name not in self.presets:
            available = ", ".join(self.presets.keys())
            embed = self.create_error_embed(f"Nieznany preset. Dostępne: {available}")
            await interaction.response.send_message(embed=embed)
            return
        
        preset = self.presets[preset_name]
        queue = self.get_queue(interaction.guild.id)
        
        # Apply preset settings
        queue.set_genre(preset["genre"])
        queue.set_theme(preset["theme"])
        if preset["language"] != "current":
            queue.set_language(preset["language"])
        
        embed = self.create_success_embed(
            f"🎨 Preset '{preset_name}' zastosowany!\n"
            f"{preset['description']}\n"
            f"Gatunek: {preset['genre']}, Temat: {preset['theme']}"
        )
        await interaction.response.send_message(embed=embed)

    # ==================== POMOCY ====================
    
    @app_commands.command(name="radio_help", description="Pokaż wszystkie komendy")
    async def radio_help(self, interaction: discord.Interaction):
        """Pokaż pomoc"""
        help_text = """
**🎵 ACE-Step Discord Radio Bot**

**Podstawowe:**
• `/radio_join` - Dołącz do kanału
• `/radio_play` - Zagraj muzykę
• `/radio_skip` - Pomiń utwór  
• `/radio_stop` - Zatrzymaj radio
• `/radio_upload` - Wrzuć plik z utworem na kanał

**Ustawienia:**
• `/radio_genre` - Ustaw gatunek
• `/radio_theme` - Ustaw temat
• `/radio_language` - Ustaw język
• `/radio_maxlength` - Maks długość

**Kolejka:**
• `/radio_auto` - Auto-dodawanie utworów
• `/radio_queue_list` - Pokaż kolejkę

**Info:**
• `/radio_settings` - Obecne ustawienia
• `/radio_nowplaying` - Co gra
• `/radio_preset` - Gotowe kombinacje
• `/radio_stats` - Statystyki bota

💡 Wszystkie parametry są opcjonalne!
        """
        
        embed = self.create_embed("📚 Pomoc", help_text.strip())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="radio_stats", description="Pokaż statystyki bota")
    async def radio_stats(self, interaction: discord.Interaction):
        """Pokaż statystyki bota"""
        metrics = get_metrics()
        if not metrics:
            embed = self.create_error_embed("Statystyki nie są dostępne")
            await interaction.response.send_message(embed=embed)
            return
        
        stats = metrics.get_summary_stats()
        uptime = stats["uptime"]
        
        embed = self.create_embed(
            "📊 Statystyki Bota",
            f"**⏱️ Czas działania:** {uptime['days']}d {uptime['hours']}h {uptime['minutes']}m\n"
            f"**🎵 Utwory wygenerowane:** {stats['generation']['total_songs']}\n"
            f"**⚡ Średni czas generowania:** {stats['generation']['avg_time']}s\n"
            f"**📈 Utworów na godzinę:** {stats['generation']['songs_per_hour']}\n"
            f"**🎮 Wykonane komendy:** {stats['activity']['total_commands']}\n"
            f"**📤 Pliki wysłane:** {stats['activity']['total_uploads']}\n"
            f"**❌ Błędy:** {stats['activity']['total_errors']}\n"
            f"**🌐 Aktywne serwery:** {stats['activity']['active_guilds']}\n"
            f"**🔊 Połączenia głosowe:** {stats['activity']['voice_connections']}\n"
            f"**💾 Szczytowe RAM:** {stats['performance']['peak_memory_mb']}MB\n"
            f"**🎯 Średnia kolejka:** {stats['performance']['avg_queue_length']}"
        )
        
        # Add popular genres/languages if available
        if stats['popular']['top_genres']:
            top_genres = ", ".join([f"{k}({v})" for k, v in list(stats['popular']['top_genres'].items())[:3]])
            embed.add_field(name="🎶 Popularne gatunki", value=top_genres, inline=True)
        
        if stats['popular']['top_languages']:
            top_languages = ", ".join([f"{k}({v})" for k, v in list(stats['popular']['top_languages'].items())[:3]])
            embed.add_field(name="🌍 Popularne języki", value=top_languages, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== HELPER METHODS ====================
    
    async def _auto_queue_task(self, guild_id: int):
        """Background task dla auto-queue"""
        try:
            while guild_id in self.voice_clients:
                queue = self.get_queue(guild_id)
                voice_client = self.voice_clients[guild_id]
                
                # Fill buffer if needed
                await queue.ensure_buffer_full(self.radio_engine)
                
                # If nothing playing and queue has tracks, play next
                if not voice_client.is_playing() and queue.queue:
                    track = queue.get_next_track()
                    if track:
                        try:
                            # Convert for Discord
                            discord_audio_path = self.radio_engine.convert_for_discord(track.path)
                            source = discord.FFmpegPCMAudio(str(discord_audio_path))
                            voice_client.play(source)
                            print(f"Auto-playing: {track.title}")
                        except Exception as e:
                            print(f"Auto-play failed: {e}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except asyncio.CancelledError:
            print(f"Auto-queue task cancelled for guild {guild_id}")
        except Exception as e:
            print(f"Auto-queue task error: {e}")

async def setup(bot):
    """Setup function dla cog"""
    await bot.add_cog(RadioCog(bot))
