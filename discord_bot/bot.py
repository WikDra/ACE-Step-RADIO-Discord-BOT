"""
Main Discord bot file for ACE-Step Radio Bot
"""

import discord
from discord.ext import commands
import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from config.settings import *
from config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from utils.metrics import init_metrics

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_radio.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== BOT SETUP ====================
class RadioBot(commands.Bot):
    def __init__(self):
        """Inicjalizacja bota"""
        
        # Intents setup
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.message_content = True
        intents.guilds = True
        
        # Bot init
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description="ACE-Step AI Radio Bot - Generuje muzykę w czasie rzeczywistym"
        )
        
        # Setup paths
        self._setup_directories()
        
        logger.info("RadioBot initialized")
    
    def _setup_directories(self):
        """Utwórz katalogi jeśli nie istnieją"""
        directories = [OUTPUT_DIR, TEMP_DIR, CACHE_DIR]
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
    
    async def setup_hook(self):
        """Setup hook - ładowanie cogs"""
        try:
            # Initialize metrics
            self.metrics = init_metrics(self)
            logger.info("Metrics collector initialized")
            
            # Załaduj RadioCog
            await self.load_extension('cogs.radio_cog')
            logger.info("RadioCog loaded successfully")
            
            # Sync slash commands
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
            
        except Exception as e:
            logger.error(f"Failed to load cogs: {e}")
            raise
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set activity status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/radio_help | AI Music Generation"
        )
        await self.change_presence(activity=activity)
        
        # Print startup info
        print("=" * 50)
        print("🎵 ACE-Step Discord Radio Bot")
        print("=" * 50)
        print(f"Bot: {self.user}")
        print(f"Guilds: {len(self.guilds)}")
        print(f"Users: {len(set(self.get_all_members()))}")
        print(f"Slash Commands: {len(self.tree.get_commands())}")
        print("=" * 50)
        print("✅ Bot is ready! Use /radio_help for commands")
        print("=" * 50)
        
        # Test model availability
        await self._test_models()
    
    async def _test_models(self):
        """Test model availability"""
        try:
            # Test FFmpeg
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ FFmpeg available")
            else:
                logger.warning("⚠️ FFmpeg not found - audio conversion may fail")
            
            # Test CUDA
            import torch
            if torch.cuda.is_available():
                logger.info(f"✅ CUDA available - {torch.cuda.get_device_name()}")
            else:
                logger.info("ℹ️ CUDA not available - using CPU")
            
            # Test model paths
            if LLM_MODEL_PATH.exists():
                logger.info(f"✅ LLM model found: {LLM_MODEL_PATH}")
            else:
                logger.warning(f"⚠️ LLM model not found: {LLM_MODEL_PATH}")
            
            if ACE_CHECKPOINT_PATH.exists():
                logger.info(f"✅ ACE-Step checkpoints found: {ACE_CHECKPOINT_PATH}")
            else:
                logger.warning(f"⚠️ ACE-Step checkpoints not found: {ACE_CHECKPOINT_PATH}")
                
        except Exception as e:
            logger.error(f"Model test failed: {e}")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do tej komendy!")
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot nie ma wymaganych uprawnień!")
        
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ Ta komenda działa tylko na serwerach!")
        
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send(f"❌ Wystąpił błąd: {str(error)}")
    
    async def on_guild_join(self, guild):
        """When bot joins a new guild"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Send welcome message to the first available text channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🎵 Dziękuję za dodanie ACE-Step Radio Bot!",
                    description=(
                        "Jestem botem do generowania muzyki AI w czasie rzeczywistym.\n\n"
                        "**Szybki start:**\n"
                        "1. Dołącz do kanału głosowego\n"
                        "2. Użyj `/radio_join`\n"
                        "3. Użyj `/radio_play`\n\n"
                        "Użyj `/radio_help` aby zobaczyć wszystkie komendy!"
                    ),
                    color=discord.Color.blue()
                )
                embed.set_footer(text="ACE-Step Radio Bot")
                
                try:
                    await channel.send(embed=embed)
                    break
                except Exception:
                    continue
    
    async def on_guild_remove(self, guild):
        """When bot leaves a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates"""
        # If bot was moved or disconnected, clean up
        if member == self.user:
            if before.channel and not after.channel:
                # Bot was disconnected
                guild_id = before.channel.guild.id
                
                # Clean up voice client reference
                cog = self.get_cog('RadioCog')
                if cog and guild_id in cog.voice_clients:
                    del cog.voice_clients[guild_id]
                
                # Cancel auto-queue task
                if cog and guild_id in cog.playing_tasks:
                    cog.playing_tasks[guild_id].cancel()
                    del cog.playing_tasks[guild_id]
                
                logger.info(f"Cleaned up after disconnect from guild {guild_id}")

# ==================== STARTUP ====================
async def main():
    """Main startup function"""
    
    # Check Discord token
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        print("❌ DISCORD_TOKEN not set!")
        print("Set your Discord bot token:")
        print("  Windows: set DISCORD_TOKEN=your_token_here")
        print("  Linux/Mac: export DISCORD_TOKEN=your_token_here")
        return
    
    # Create bot instance
    bot = RadioBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(bot.close())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start bot
        logger.info("Starting Discord bot...")
        await bot.start(DISCORD_TOKEN)
    
    except discord.LoginFailure:
        logger.error("Failed to login - check your Discord token!")
        print("❌ Login failed! Check your DISCORD_TOKEN")
    
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        print(f"❌ Startup failed: {e}")
    
    finally:
        # Cleanup
        if not bot.is_closed():
            # Stop metrics collection
            if hasattr(bot, 'metrics'):
                bot.metrics.stop_monitoring()
            await bot.close()
        logger.info("Bot shutdown complete")

def check_dependencies():
    """Check if all dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required packages
    required_packages = [
        'discord.py',
        'torch',
        'transformers',
        'llama_cpp',
        'librosa',
        'soundfile'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').replace('.py', ''))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    # Check FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg")
        else:
            print("⚠️ FFmpeg not found (audio conversion may fail)")
    except FileNotFoundError:
        print("⚠️ FFmpeg not found (audio conversion may fail)")
    
    print("✅ Dependency check complete\n")
    return True

if __name__ == "__main__":
    """Entry point"""
    
    print("🎵 ACE-Step Discord Radio Bot")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed!")
        sys.exit(1)
    
    # Check environment
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN environment variable not set!")
        print("\nTo set your token:")
        print("  Windows: set DISCORD_TOKEN=your_token_here")
        print("  Linux/Mac: export DISCORD_TOKEN=your_token_here")
        sys.exit(1)
    
    # Run bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
