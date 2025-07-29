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
where conda >nul 2>&1
if errorlevel 1 (
    echo ❌ BŁĄD: Conda nie znaleziona!
    echo.
    echo ⚠️ WAŻNE: Ten projekt wymaga Conda do prawidłowej instalacji PyTorch z CUDA
    echo.
    echo 📥 Zainstaluj Miniconda lub Anaconda:
    echo   - Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo   - Anaconda: https://www.anaconda.com/download
    echo.
    echo 🔄 Po instalacji uruchom ponownie ten skrypt
    pause
    exit /b 1
) else (
    echo ✅ Conda znaleziona
    set USE_CONDA=true
)

REM 3. Tworzenie środowiska
echo [3/6] Sprawdzanie środowiska Python...
conda env list | findstr "ace-radio" >nul 2>&1
if errorlevel 1 (
    echo Tworzenie nowego środowiska Conda...
    conda create -n ace-radio python=3.10 -y
) else (
    echo ✅ Środowisko ace-radio już istnieje
)

echo [4/6] Instalowanie PyTorch z CUDA...
conda install -n ace-radio pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

REM 4. Instalowanie zależności Discord
echo [5/6] Instalowanie zależności Discord...
conda run -n ace-radio pip install -r requirements_discord.txt

REM 5. Instalowanie ACE-Step
echo [6/6] Instalowanie ACE-Step...
conda run -n ace-radio pip install -e .

REM 6. Sprawdzanie FFmpeg
echo [7/8] Sprawdzanie FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FFmpeg nie znaleziony!
    echo Pobierz FFmpeg z: https://ffmpeg.org/download.html
    echo I dodaj do PATH
)

REM 7. Tworzenie pliku .env
echo.
echo [8/8] Konfiguracja...
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
echo   conda activate ace-radio
echo.
pause
