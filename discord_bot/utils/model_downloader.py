"""
Model downloader for ACE-Step Discord Bot
Automatically downloads required models if they don't exist
"""

import os
import requests
from pathlib import Path
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

def download_file(url: str, destination: Path, description: str = None) -> bool:
    """
    Download a file with progress bar
    
    Args:
        url: URL to download from
        destination: Path where to save the file
        description: Description for progress bar
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if destination.exists():
            logger.info(f"✅ File already exists: {destination.name}")
            return True
            
        logger.info(f"🔄 Downloading {description or destination.name}...")
        
        # Download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as file, tqdm(
            desc=description or destination.name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = file.write(chunk)
                pbar.update(size)
                
        logger.info(f"✅ Downloaded: {destination.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {url}: {e}")
        if destination.exists():
            destination.unlink()  # Remove partial file
        return False

def download_llm_model(models_dir: Path) -> bool:
    """
    Download Huihui-gemma LLM model for lyrics generation
    
    Args:
        models_dir: Directory where models should be stored
        
    Returns:
        bool: True if successful
    """
    # Import here to avoid circular imports
    from ..config.settings import LLM_MODEL_URL, LLM_MODEL_NAME
    
    model_file = models_dir / LLM_MODEL_NAME
    
    return download_file(
        url=LLM_MODEL_URL,
        destination=model_file,
        description="Huihui-gemma LLM Model (for lyrics generation)"
    )

def download_ace_step_models(models_dir: Path) -> bool:
    """
    Download ACE-Step checkpoint files
    
    Args:
        models_dir: Directory where models should be stored
        
    Returns:
        bool: True if successful
    """
    # ACE-Step model URLs - you'll need to provide these
    ace_step_urls = {
        # Add official ACE-Step model URLs here when available
        # "ace_step_model.pth": "https://...",
        # "ace_step_config.json": "https://...",
    }
    
    if not ace_step_urls:
        logger.warning("⚠️ ACE-Step model URLs not configured")
        logger.info("📋 Please manually download ACE-Step models to:")
        logger.info(f"   {models_dir}")
        logger.info("📖 Check ACE-Step documentation for model download instructions")
        return False
    
    success = True
    for filename, url in ace_step_urls.items():
        model_file = models_dir / filename
        if not download_file(url, model_file, f"ACE-Step {filename}"):
            success = False
            
    return success

def ensure_models_available(models_dir: Path) -> tuple[bool, bool]:
    """
    Ensure all required models are available, download if needed
    
    Args:
        models_dir: Directory where models should be stored
        
    Returns:
        tuple[bool, bool]: (llm_available, ace_step_available)
    """
    logger.info("🔍 Checking model availability...")
    
    # Check LLM model
    from ..config.settings import LLM_MODEL_NAME
    llm_file = models_dir / LLM_MODEL_NAME
    llm_available = llm_file.exists()
    
    if not llm_available:
        logger.info("📥 LLM model not found, downloading...")
        llm_available = download_llm_model(models_dir)
    else:
        logger.info(f"✅ LLM model found: {llm_file.name}")
    
    # Check ACE-Step models (basic check for any .pth or .bin files)
    ace_step_files = list(models_dir.glob("*.pth")) + list(models_dir.glob("*.bin")) + list(models_dir.glob("*.safetensors"))
    ace_step_available = len(ace_step_files) > 0
    
    if not ace_step_available:
        logger.info("📥 ACE-Step models not found, attempting download...")
        ace_step_available = download_ace_step_models(models_dir)
    else:
        logger.info(f"✅ ACE-Step models found: {len(ace_step_files)} files")
    
    return llm_available, ace_step_available

def check_model_space(models_dir: Path) -> None:
    """
    Check available disk space for model downloads
    
    Args:
        models_dir: Directory where models will be stored
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage(models_dir.parent)
        free_gb = free // (1024**3)
        
        logger.info(f"💾 Available disk space: {free_gb}GB")
        
        if free_gb < 5:
            logger.warning("⚠️ Low disk space! Models require ~3-4GB")
        elif free_gb < 2:
            logger.error("❌ Insufficient disk space for model downloads")
            
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")

if __name__ == "__main__":
    # Test download functionality
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from discord_bot.config.settings import MODELS_DIR
    
    logging.basicConfig(level=logging.INFO)
    
    print("🎵 ACE-Step Model Downloader")
    print("=" * 40)
    
    check_model_space(MODELS_DIR)
    llm_ok, ace_ok = ensure_models_available(MODELS_DIR)
    
    print("\n📊 Model Status:")
    print(f"LLM Model: {'✅' if llm_ok else '❌'}")
    print(f"ACE-Step Models: {'✅' if ace_ok else '❌'}")
    
    if llm_ok and ace_ok:
        print("\n🎉 All models ready!")
    else:
        print("\n⚠️ Some models missing - bot may have limited functionality")
