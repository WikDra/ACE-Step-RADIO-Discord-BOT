# Jak stworzyć branche beta i release/1dev

## Szybka instrukcja

```bash
# 1. Pobierz ten PR
git fetch origin copilot/cleanup-readme-and-add-linux-installer

# 2. Stwórz branch beta z commita 77fe968
git checkout -b beta 77fe968

# 3. Wypchnij beta na GitHub
git push -u origin beta

# 4. Stwórz branch release/1dev z commita e8ecbcc
git checkout -b release/1dev e8ecbcc

# 5. Wypchnij release/1dev na GitHub
git push -u origin release/1dev
```

## Commit hashes (do skopiowania)

- **Beta branch**: `77fe968` (zawiera wszystkie zmiany: Linux installer, angielski interfejs, nowe presety)
- **Release/1dev branch**: `e8ecbcc` (bazowa wersja przed zmianami)

## Alternatywna metoda (jeśli nie możesz użyć commit hash)

```bash
# Pobierz PR jako lokalny branch
git fetch origin copilot/cleanup-readme-and-add-linux-installer:temp-pr

# Beta = temp-pr minus ostatnie 3 commity (6a7762f, a5a66b7, 3feecb2)
git checkout -b beta temp-pr~3

# Push beta
git push -u origin beta

# Release/1dev z base commita
git checkout -b release/1dev e8ecbcc

# Push release/1dev
git push -u origin release/1dev

# Usuń temporary branch
git branch -D temp-pr
```

## Co zawiera każdy branch?

### Beta (commit 77fe968)
✅ Setup.sh - instalator dla Linuxa
✅ Angielski interfejs (BOT_LANGUAGE=english)
✅ 6 nowych presetów muzycznych
✅ 5 nowych gatunków
✅ 4 nowe motywy
✅ Dokumentacja (IMPROVEMENTS.md, CHANGELOG.md, TESTING.md, etc.)

### Release/1dev (commit e8ecbcc)
✅ Bazowa wersja przed wszystkimi zmianami
✅ Stable baseline

## Sprawdzenie czy się udało

```bash
# Zobacz wszystkie branche
git branch -a

# Powinieneś zobaczyć:
#   origin/beta
#   origin/release/1dev
```
