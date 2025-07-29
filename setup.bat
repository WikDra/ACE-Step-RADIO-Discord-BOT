@echo off
echo 🎵 ACE-Step Discord Radio Setup
echo.

REM 1. Sprawdź czy jesteśmy w poprawnym katalogu
if not exist "radio_gradio.py" (
    echo ❌ Błąd: Plik radio_gradio.py nie znaleziony!
    echo Upewnij się, że jesteś w katalogu ACE-Step-RADIO
    pause
    exit /b 1
)

REM 2. Sprawdź czy Discord bot katalog istnieje
if not exist "discord_bot" (
    echo ❌ Błąd: Katalog discord_bot nie znaleziony!
    echo Najpierw utwórz strukturę Discord bota
    pause
    exit /b 1
)

echo [1/6] Sprawdzanie środowiska Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nie znaleziony! Zainstaluj Python 3.8+
    pause
    exit /b 1
)

echo [2/6] Sprawdzanie Conda...
conda --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Conda nie znaleziona - używam pip zamiast conda
    set USE_CONDA=false
) else (
    set USE_CONDA=true
)

REM 3. Tworzenie środowiska
echo [3/6] Tworzenie środowiska Python...
if "%USE_CONDA%"=="true" (
    echo Tworzenie środowiska Conda...
    conda create -n ace-radio python=3.10 -y
    call conda activate ace-radio
    
    echo Instalowanie PyTorch z CUDA...
    conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
) else (
    echo Tworzenie venv...
    python -m venv ace-radio-venv
    call ace-radio-venv\Scripts\activate.bat
    
    echo Instalowanie PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
)

REM 4. Instalowanie zależności Discord
echo [4/6] Instalowanie zależności Discord...
pip install -r requirements_discord.txt

REM 5. Instalowanie ACE-Step
echo [5/6] Instalowanie ACE-Step...
pip install -e .

REM 6. Sprawdzanie FFmpeg
echo [6/6] Sprawdzanie FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FFmpeg nie znaleziony!
    echo Pobierz FFmpeg z: https://ffmpeg.org/download.html
    echo I dodaj do PATH
)

REM 7. Tworzenie pliku .env
echo.
echo [7/7] Konfiguracja...
if not exist ".env" (
    echo Tworzenie pliku .env...
    echo DISCORD_TOKEN=TWOJ_TOKEN_TUTAJ > .env
    echo.
    echo ⚠️ WAŻNE: Ustaw swój Discord token w pliku .env
)

echo.
echo ✅ Setup zakończony!
echo.
echo 📋 Następne kroki:
echo 1. Ustaw DISCORD_TOKEN w pliku .env
echo 2. Pobierz modele ACE-Step (jeśli jeszcze nie masz)
echo 3. Uruchom bota: python discord_bot/bot.py
echo.
echo 🔧 Aktywacja środowiska:
if "%USE_CONDA%"=="true" (
    echo   conda activate ace-radio
) else (
    echo   ace-radio-venv\Scripts\activate.bat
)
echo.
pause
