"""
Metrics i monitoring dla ACE-Step Discord Bot
"""

import json
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class BotMetrics:
    """Struktura metryk bota"""
    # Counters
    total_songs_generated: int = 0
    total_commands_executed: int = 0
    total_uploads: int = 0
    total_errors: int = 0
    
    # Performance
    avg_generation_time: float = 0.0
    avg_queue_length: float = 0.0
    
    # System
    peak_memory_usage: float = 0.0
    peak_gpu_memory: float = 0.0
    
    # Activity
    active_guilds: int = 0
    active_voice_connections: int = 0
    
    # Timestamps
    bot_start_time: str = ""
    last_update_time: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BotMetrics':
        """Create from dictionary"""
        return cls(**data)

class MetricsCollector:
    """Collector metryk dla bota Discord"""
    
    def __init__(self, bot):
        self.bot = bot
        self.metrics = BotMetrics()
        self.metrics.bot_start_time = datetime.now().isoformat()
        
        # Statistics storage
        self.generation_times: List[float] = []
        self.queue_lengths: List[int] = []
        self.genre_stats: Dict[str, int] = {}
        self.language_stats: Dict[str, int] = {}
        self.command_stats: Dict[str, int] = {}
        self.error_stats: Dict[str, int] = {}
        
        # File paths
        self.metrics_file = Path("bot_metrics.json")
        self.stats_file = Path("bot_statistics.json")
        
        # Monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Load existing data
        self.load_metrics()
    
    def record_song_generation(self, genre: str, language: str, generation_time: float):
        """Zapisz generowanie utworu"""
        self.metrics.total_songs_generated += 1
        self.generation_times.append(generation_time)
        
        # Update average (rolling window of last 100)
        if len(self.generation_times) > 100:
            self.generation_times.pop(0)
        self.metrics.avg_generation_time = sum(self.generation_times) / len(self.generation_times)
        
        # Update genre/language stats
        self.genre_stats[genre] = self.genre_stats.get(genre, 0) + 1
        self.language_stats[language] = self.language_stats.get(language, 0) + 1
        
        self.metrics.last_update_time = datetime.now().isoformat()
    
    def record_command_execution(self, command_name: str):
        """Zapisz wykonanie komendy"""
        self.metrics.total_commands_executed += 1
        self.command_stats[command_name] = self.command_stats.get(command_name, 0) + 1
        self.metrics.last_update_time = datetime.now().isoformat()
    
    def record_upload(self):
        """Zapisz upload pliku"""
        self.metrics.total_uploads += 1
        self.metrics.last_update_time = datetime.now().isoformat()
    
    def record_error(self, error_type: str):
        """Zapisz błąd"""
        self.metrics.total_errors += 1
        self.error_stats[error_type] = self.error_stats.get(error_type, 0) + 1
        self.metrics.last_update_time = datetime.now().isoformat()
    
    def update_queue_length(self, guild_id: int, queue_length: int):
        """Aktualizuj długość kolejki"""
        self.queue_lengths.append(queue_length)
        
        # Rolling window
        if len(self.queue_lengths) > 1000:
            self.queue_lengths.pop(0)
        
        if self.queue_lengths:
            self.metrics.avg_queue_length = sum(self.queue_lengths) / len(self.queue_lengths)
    
    def update_guild_stats(self):
        """Aktualizuj statystyki serwerów"""
        self.metrics.active_guilds = len(self.bot.guilds)
        
        # Count voice connections
        voice_connections = 0
        cog = self.bot.get_cog('RadioCog')
        if cog:
            voice_connections = len(cog.voice_clients)
        self.metrics.active_voice_connections = voice_connections
    
    def _monitor_system_resources(self):
        """Monitoruj zasoby systemowe"""
        try:
            # Memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > self.metrics.peak_memory_usage:
                self.metrics.peak_memory_usage = memory_mb
            
            # GPU memory (if available)
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
                    if gpu_memory_mb > self.metrics.peak_gpu_memory:
                        self.metrics.peak_gpu_memory = gpu_memory_mb
            except ImportError:
                pass
                
        except Exception as e:
            print(f"Resource monitoring error: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update system resources
                self._monitor_system_resources()
                
                # Update guild stats
                self.update_guild_stats()
                
                # Save metrics every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.save_metrics()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(30)  # Longer delay on error
    
    def get_uptime(self) -> timedelta:
        """Pobierz czas działania bota"""
        start_time = datetime.fromisoformat(self.metrics.bot_start_time)
        return datetime.now() - start_time
    
    def get_summary_stats(self) -> Dict:
        """Pobierz podsumowanie statystyk"""
        uptime = self.get_uptime()
        
        return {
            "uptime": {
                "total_seconds": uptime.total_seconds(),
                "days": uptime.days,
                "hours": uptime.seconds // 3600,
                "minutes": (uptime.seconds % 3600) // 60
            },
            "generation": {
                "total_songs": self.metrics.total_songs_generated,
                "avg_time": round(self.metrics.avg_generation_time, 2),
                "songs_per_hour": round(self.metrics.total_songs_generated / (uptime.total_seconds() / 3600), 2) if uptime.total_seconds() > 0 else 0
            },
            "activity": {
                "total_commands": self.metrics.total_commands_executed,
                "total_uploads": self.metrics.total_uploads,
                "total_errors": self.metrics.total_errors,
                "active_guilds": self.metrics.active_guilds,
                "voice_connections": self.metrics.active_voice_connections
            },
            "performance": {
                "peak_memory_mb": round(self.metrics.peak_memory_usage, 1),
                "peak_gpu_memory_mb": round(self.metrics.peak_gpu_memory, 1),
                "avg_queue_length": round(self.metrics.avg_queue_length, 1)
            },
            "popular": {
                "top_genres": dict(sorted(self.genre_stats.items(), key=lambda x: x[1], reverse=True)[:5]),
                "top_languages": dict(sorted(self.language_stats.items(), key=lambda x: x[1], reverse=True)[:5]),
                "top_commands": dict(sorted(self.command_stats.items(), key=lambda x: x[1], reverse=True)[:10])
            }
        }
    
    def get_detailed_stats(self) -> Dict:
        """Pobierz szczegółowe statystyki"""
        summary = self.get_summary_stats()
        
        return {
            **summary,
            "detailed": {
                "all_genres": self.genre_stats,
                "all_languages": self.language_stats,
                "all_commands": self.command_stats,
                "error_breakdown": self.error_stats,
                "recent_generation_times": self.generation_times[-20:],  # Last 20
                "recent_queue_lengths": self.queue_lengths[-50:]  # Last 50
            },
            "metrics": self.metrics.to_dict()
        }
    
    def save_metrics(self):
        """Zapisz metryki do pliku"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics.to_dict(), f, indent=2, ensure_ascii=False)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                stats = {
                    "generation_times": self.generation_times,
                    "queue_lengths": self.queue_lengths,
                    "genre_stats": self.genre_stats,
                    "language_stats": self.language_stats,
                    "command_stats": self.command_stats,
                    "error_stats": self.error_stats,
                    "last_saved": datetime.now().isoformat()
                }
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Failed to save metrics: {e}")
    
    def load_metrics(self):
        """Załaduj metryki z pliku"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Don't overwrite start time
                    start_time = self.metrics.bot_start_time
                    self.metrics = BotMetrics.from_dict(data)
                    if not self.metrics.bot_start_time:
                        self.metrics.bot_start_time = start_time
            
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.generation_times = data.get("generation_times", [])
                    self.queue_lengths = data.get("queue_lengths", [])
                    self.genre_stats = data.get("genre_stats", {})
                    self.language_stats = data.get("language_stats", {})
                    self.command_stats = data.get("command_stats", {})
                    self.error_stats = data.get("error_stats", {})
                    
        except Exception as e:
            print(f"Failed to load metrics: {e}")
    
    def reset_metrics(self):
        """Zresetuj wszystkie metryki"""
        self.metrics = BotMetrics()
        self.metrics.bot_start_time = datetime.now().isoformat()
        self.generation_times.clear()
        self.queue_lengths.clear()
        self.genre_stats.clear()
        self.language_stats.clear()
        self.command_stats.clear()
        self.error_stats.clear()
        print("Metrics reset")
    
    def stop_monitoring(self):
        """Zatrzymaj monitoring"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.save_metrics()

# Global metrics instance (will be set by bot)
metrics_collector: Optional[MetricsCollector] = None

def get_metrics() -> Optional[MetricsCollector]:
    """Get global metrics collector"""
    return metrics_collector

def init_metrics(bot) -> MetricsCollector:
    """Initialize global metrics collector"""
    global metrics_collector
    metrics_collector = MetricsCollector(bot)
    return metrics_collector
