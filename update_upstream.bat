@echo off
echo 🔄 Aktualizacja do najnowszego ACE-Step
echo.

REM Sprawdź czy jesteśmy w repo git
if not exist ".git" (
    echo ❌ To nie jest repozytorium git!
    pause
    exit /b 1
)

echo [1/5] Sprawdzanie stanu repozytorium...
git status --porcelain > temp_status.txt
for /f %%i in ("temp_status.txt") do set size=%%~zi
del temp_status.txt

if %size% gtr 0 (
    echo ⚠️ Masz niezapisane zmiany!
    echo Zapisz zmiany przed aktualizacją:
    echo   git add .
    echo   git commit -m "Save local changes"
    pause
    exit /b 1
)

echo [2/5] Dodawanie upstream (jeśli nie istnieje)...
git remote get-url upstream >nul 2>&1
if errorlevel 1 (
    echo Dodawanie remote upstream...
    git remote add upstream https://github.com/ace-step/ACE-Step.git
) else (
    echo Upstream już istnieje
)

echo [3/5] Pobieranie najnowszych zmian z upstream...
git fetch upstream
if errorlevel 1 (
    echo ❌ Błąd pobierania z upstream!
    pause
    exit /b 1
)

echo [4/5] Mergowanie zmian z upstream/main...
git merge upstream/main
if errorlevel 1 (
    echo ⚠️ Konflikty podczas merge!
    echo Rozwiąż konflikty ręcznie, a następnie:
    echo   git add .
    echo   git commit -m "Resolve merge conflicts"
    pause
    exit /b 1
)

echo [5/5] Aktualizacja zależności...
if exist "requirements_discord.txt" (
    echo Aktualizacja pakietów Discord...
    pip install -r requirements_discord.txt --upgrade
)

if exist "requirements.txt" (
    echo Aktualizacja pakietów ACE-Step...
    pip install -r requirements.txt --upgrade
)

echo Reinstalacja ACE-Step...
pip install -e . --upgrade

echo.
echo ✅ Aktualizacja zakończona pomyślnie!
echo.
echo 📋 Co dalej:
echo 1. Sprawdź czy Discord bot nadal działa: python discord_bot/bot.py
echo 2. Przetestuj generowanie muzyki
echo 3. Sprawdź logi pod kątem błędów
echo.
echo 🔍 W razie problemów:
echo - Sprawdź discord_radio.log
echo - Uruchom testy: python -m pytest test_radio_bot.py
echo - Sprawdź konfigurację: discord_bot/config/settings.py
echo.
pause
