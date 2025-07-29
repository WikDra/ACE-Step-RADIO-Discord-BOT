@echo off
echo 🎵 ACE-Step Discord Radio Setup (Advanced - pip only)
echo.
echo ⚠️ UWAGA: Ten skrypt używa pip zamiast conda!
echo ⚠️ Może powodować konflikty zależności z PyTorch/CUDA
echo ⚠️ Zalecamy użycie setup.bat z conda
echo.
set /p continue="Czy kontynuować? (tak/nie): "
if /i not "%continue%"=="tak" (
    echo Anulowano. Użyj setup.bat dla bezpiecznej instalacji.
    pause
    exit /b 0
)

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

echo [2/6] Tworzenie venv...
python -m venv ace-radio-venv
call ace-radio-venv\Scripts\activate.bat

echo [3/6] Aktualizacja pip...
python -m pip install --upgrade pip

echo [4/6] Instalowanie PyTorch (może być niestabilne!)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo [5/6] Instalowanie zależności Discord...
pip install -r requirements_discord.txt

echo [6/6] Instalowanie ACE-Step...
pip install -e .

REM Sprawdzanie FFmpeg
echo [7/7] Sprawdzanie FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FFmpeg nie znaleziony!
    echo Pobierz FFmpeg z: https://ffmpeg.org/download.html
    echo I dodaj do PATH
)

REM Tworzenie pliku .env
echo.
echo [8/8] Konfiguracja...
if not exist ".env" (
    echo Tworzenie pliku .env...
    echo DISCORD_TOKEN=TWOJ_TOKEN_TUTAJ > .env
    echo.
    echo ⚠️ WAŻNE: Ustaw swój Discord token w pliku .env
)

echo.
echo ⚠️ Setup zakończony (pip version)!
echo ⚠️ UWAGA: W przypadku problemów użyj setup.bat z conda
echo.
echo 📋 Następne kroki:
echo 1. Ustaw DISCORD_TOKEN w pliku .env
echo 2. Pobierz modele ACE-Step (jeśli jeszcze nie masz)
echo 3. Uruchom bota: python discord_bot/bot.py
echo.
echo 🔧 Aktywacja środowiska:
echo   ace-radio-venv\Scripts\activate.bat
echo.
pause
