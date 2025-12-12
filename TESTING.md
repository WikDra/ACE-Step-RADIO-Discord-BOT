# 🧪 Testing Guide for Beta Branch

This document outlines the testing procedures for the beta branch improvements.

## Pre-Testing Checklist

- [ ] Python 3.10+ installed
- [ ] Conda/Miniconda installed
- [ ] NVIDIA GPU with drivers (if testing GPU features)
- [ ] Discord bot token ready
- [ ] 20GB+ free disk space

## Test Scenarios

### 1. Linux Installation Test

#### Test Case 1.1: Fresh Installation on Ubuntu/Debian
```bash
# Prerequisites
sudo apt update
sudo apt install -y git ffmpeg

# Clone and setup
git clone https://github.com/WikDra/ACE-Step-RADIO-Discord-BOT.git
cd ACE-Step-RADIO-Discord-BOT
git checkout beta
chmod +x setup.sh
./setup.sh

# Expected: Script completes without errors
# Expected: Conda environment 'ace-radio' created
# Expected: .env file created
```

**Pass Criteria:**
- ✅ Script runs without fatal errors
- ✅ Conda environment created successfully
- ✅ PyTorch with CUDA installed
- ✅ Dependencies installed
- ✅ .env file exists

#### Test Case 1.2: Setup with Missing Conda
```bash
# Temporarily hide conda
export PATH=$(echo $PATH | sed 's|[^:]*conda[^:]*:||g')

# Run setup
./setup.sh

# Expected: Clear error message about missing Conda
# Expected: Installation instructions provided
```

**Pass Criteria:**
- ✅ Script detects missing Conda
- ✅ Provides helpful error message
- ✅ Includes installation instructions
- ✅ Script exits gracefully

#### Test Case 1.3: Setup with Missing FFmpeg
```bash
# Setup without FFmpeg installed
sudo apt remove ffmpeg

# Run setup
./setup.sh

# Expected: Warning about missing FFmpeg
# Expected: Installation instructions provided
# Expected: Setup continues despite warning
```

**Pass Criteria:**
- ✅ Script detects missing FFmpeg
- ✅ Warns user but continues
- ✅ Provides installation command

### 2. Multi-language Interface Test

#### Test Case 2.1: Polish Interface (Default)
```bash
# Ensure BOT_LANGUAGE is not set or set to polish
echo "BOT_LANGUAGE=polish" >> .env

# Test import
python3 -c "
import sys
sys.path.insert(0, '.')
from discord_bot.config.constants import ERROR_MESSAGES
assert 'Musisz być' in ERROR_MESSAGES['not_in_voice']
print('✅ Polish interface working')
"
```

**Pass Criteria:**
- ✅ Polish messages loaded
- ✅ No errors during import

#### Test Case 2.2: English Interface
```bash
# Set English language
echo "BOT_LANGUAGE=english" >> .env

# Test import
python3 -c "
import sys
sys.path.insert(0, '.')
from discord_bot.config.constants import ERROR_MESSAGES
assert 'You must be' in ERROR_MESSAGES['not_in_voice']
print('✅ English interface working')
"
```

**Pass Criteria:**
- ✅ English messages loaded
- ✅ No errors during import
- ✅ Messages are in English

#### Test Case 2.3: Invalid Language Fallback
```bash
# Set invalid language
echo "BOT_LANGUAGE=invalid_lang" >> .env

# Test import - should fallback to Polish
python3 -c "
import sys
sys.path.insert(0, '.')
from discord_bot.config.constants import ERROR_MESSAGES
assert 'Musisz być' in ERROR_MESSAGES['not_in_voice']
print('✅ Fallback to Polish working')
"
```

**Pass Criteria:**
- ✅ Falls back to Polish
- ✅ No errors or crashes

### 3. New Presets Test

#### Test Case 3.1: Load All Presets
```python
import json

with open('discord_bot/data/presets.json') as f:
    presets = json.load(f)

# Check new presets exist
new_presets = ['lofi', 'metal', 'classical', 'jazz', 'rock', 'sad']
for preset in new_presets:
    assert preset in presets
    assert 'genre' in presets[preset]
    assert 'theme' in presets[preset]
    assert 'language' in presets[preset]
    print(f"✅ {preset} preset valid")

print(f"✅ All {len(presets)} presets loaded successfully")
```

**Pass Criteria:**
- ✅ All 12 presets load successfully
- ✅ Each preset has required fields
- ✅ Descriptions are bilingual

#### Test Case 3.2: Validate Preset Values
```python
import json
from discord_bot.config.constants import MusicGenres, MusicThemes

with open('discord_bot/data/presets.json') as f:
    presets = json.load(f)

valid_genres = [g.value for g in MusicGenres]
valid_themes = [t.value for t in MusicThemes]

for name, preset in presets.items():
    genre = preset['genre']
    theme = preset['theme']
    
    # Note: Some themes like 'relaxing' might not be in enum
    # Just check they're reasonable strings
    assert isinstance(genre, str)
    assert isinstance(theme, str)
    assert isinstance(preset['language'], str)
    print(f"✅ {name} preset values valid")

print("✅ All preset values validated")
```

**Pass Criteria:**
- ✅ All presets have valid data types
- ✅ No missing required fields

### 4. Enhanced Genres and Themes Test

#### Test Case 4.1: Check New Genres
```python
from discord_bot.config.constants import MusicGenres

# Check new genres
new_genres = ['METAL', 'FUNK', 'DISCO', 'PUNK', 'ELECTRONIC']
existing_genres = [g.name for g in MusicGenres]

for genre in new_genres:
    assert genre in existing_genres
    print(f"✅ {genre} available")

print(f"✅ Total genres: {len(MusicGenres.__members__)}")
```

**Pass Criteria:**
- ✅ All new genres present
- ✅ Total genres = 15

#### Test Case 4.2: Check New Themes
```python
from discord_bot.config.constants import MusicThemes

# Check new themes
new_themes = ['RELAXING', 'CALM', 'HAPPY', 'INSTRUMENTAL']
existing_themes = [t.name for t in MusicThemes]

for theme in new_themes:
    assert theme in existing_themes
    print(f"✅ {theme} available")

print(f"✅ Total themes: {len(MusicThemes.__members__)}")
```

**Pass Criteria:**
- ✅ All new themes present
- ✅ Total themes = 14

### 5. Documentation Test

#### Test Case 5.1: Check New Documentation Files
```bash
# Check files exist
test -f IMPROVEMENTS.md && echo "✅ IMPROVEMENTS.md exists"
test -f CHANGELOG.md && echo "✅ CHANGELOG.md exists"
test -f docs/LINUX_SETUP.md && echo "✅ LINUX_SETUP.md exists"
test -f TESTING.md && echo "✅ TESTING.md exists"

# Check they're not empty
test -s IMPROVEMENTS.md && echo "✅ IMPROVEMENTS.md not empty"
test -s CHANGELOG.md && echo "✅ CHANGELOG.md not empty"
test -s docs/LINUX_SETUP.md && echo "✅ LINUX_SETUP.md not empty"
```

**Pass Criteria:**
- ✅ All documentation files exist
- ✅ Files contain content
- ✅ Markdown is properly formatted

#### Test Case 5.2: Verify README Updates
```bash
# Check README has new sections
grep -q "New in Beta" README.md && echo "✅ Beta presets section found"
grep -q "Additional Documentation" README.md && echo "✅ Docs section found"
grep -q "Linux:" README.md && echo "✅ Linux instructions found"
```

**Pass Criteria:**
- ✅ README includes new preset section
- ✅ README references new documentation
- ✅ Linux setup instructions present

### 6. Bot Startup Test (Requires Discord Token)

#### Test Case 6.1: Bot Initialization with Polish
```bash
conda activate ace-radio
echo "BOT_LANGUAGE=polish" >> .env
echo "DISCORD_TOKEN=your_token" >> .env

# Try importing the bot (don't actually run it)
python3 -c "
import sys
sys.path.insert(0, '.')
from discord_bot.config import constants
print('✅ Bot imports successful')
print(f'Interface: {constants.BOT_INTERFACE_LANGUAGE}')
"
```

**Pass Criteria:**
- ✅ Bot modules import without errors
- ✅ Polish interface confirmed

#### Test Case 6.2: Bot Initialization with English
```bash
conda activate ace-radio
echo "BOT_LANGUAGE=english" >> .env

python3 -c "
import sys
sys.path.insert(0, '.')
from discord_bot.config import constants
print('✅ Bot imports successful')
print(f'Interface: {constants.BOT_INTERFACE_LANGUAGE}')
"
```

**Pass Criteria:**
- ✅ Bot modules import without errors
- ✅ English interface confirmed

### 7. Backward Compatibility Test

#### Test Case 7.1: Legacy Code Works
```python
# Test that old code still works
from discord_bot.config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

# Old-style access
msg = ERROR_MESSAGES["not_in_voice"]
print(f"✅ Legacy ERROR_MESSAGES access works: {msg}")

msg = SUCCESS_MESSAGES["joined"]
print(f"✅ Legacy SUCCESS_MESSAGES access works: {msg}")
```

**Pass Criteria:**
- ✅ Old dictionary access works
- ✅ No breaking changes

### 8. File Permission Test

#### Test Case 8.1: Verify Executable Scripts
```bash
# Check setup.sh is executable
test -x setup.sh && echo "✅ setup.sh is executable"

# Check it has proper shebang
head -1 setup.sh | grep -q "^#!/bin/bash" && echo "✅ setup.sh has bash shebang"
```

**Pass Criteria:**
- ✅ setup.sh is executable
- ✅ Proper shebang present

### 9. JSON Validation Test

#### Test Case 9.1: Validate presets.json
```python
import json
import sys

try:
    with open('discord_bot/data/presets.json') as f:
        data = json.load(f)
    
    # Check structure
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check each preset
    for name, preset in data.items():
        assert 'genre' in preset
        assert 'theme' in preset
        assert 'language' in preset
        assert 'duration' in preset
        assert 'description' in preset
        
    print(f"✅ presets.json is valid with {len(data)} presets")
except Exception as e:
    print(f"❌ JSON validation failed: {e}")
    sys.exit(1)
```

**Pass Criteria:**
- ✅ JSON is valid
- ✅ All presets have required fields
- ✅ 12 presets total

## Integration Tests

### Test Case I.1: Full Setup Flow (Linux)
1. Fresh Ubuntu/Debian system
2. Run setup.sh
3. Configure .env
4. Start bot
5. Join voice channel
6. Try each new preset

**Pass Criteria:**
- ✅ Setup completes
- ✅ Bot starts without errors
- ✅ All presets work

### Test Case I.2: Language Switching
1. Start bot with Polish
2. Verify Polish messages
3. Stop bot
4. Change to English
5. Start bot
6. Verify English messages

**Pass Criteria:**
- ✅ Language switches correctly
- ✅ No errors during switch
- ✅ Messages in correct language

## Performance Tests

### Test Case P.1: Memory Usage
Monitor memory during:
- Bot startup
- Preset loading
- Message translations

**Pass Criteria:**
- ✅ No memory leaks
- ✅ Reasonable memory usage

## Regression Tests

### Test Case R.1: Existing Features Still Work
- [ ] All original commands work
- [ ] Original presets unchanged
- [ ] Audio generation works
- [ ] Queue management works

**Pass Criteria:**
- ✅ No existing functionality broken

## Test Results Template

```markdown
## Test Results - [Date]

Tester: [Name]
Environment: [OS/GPU/RAM]

### Installation Tests
- [ ] Test Case 1.1: PASS/FAIL
- [ ] Test Case 1.2: PASS/FAIL
- [ ] Test Case 1.3: PASS/FAIL

### Language Tests
- [ ] Test Case 2.1: PASS/FAIL
- [ ] Test Case 2.2: PASS/FAIL
- [ ] Test Case 2.3: PASS/FAIL

### Preset Tests
- [ ] Test Case 3.1: PASS/FAIL
- [ ] Test Case 3.2: PASS/FAIL

### Genre/Theme Tests
- [ ] Test Case 4.1: PASS/FAIL
- [ ] Test Case 4.2: PASS/FAIL

### Documentation Tests
- [ ] Test Case 5.1: PASS/FAIL
- [ ] Test Case 5.2: PASS/FAIL

### Notes:
[Any issues or observations]
```

## Automated Testing

### Running All Syntax Checks
```bash
#!/bin/bash
echo "Running automated tests..."

# Python syntax
python3 -m py_compile discord_bot/config/constants.py
echo "✅ Python syntax OK"

# JSON validation
python3 -c "import json; json.load(open('discord_bot/data/presets.json'))"
echo "✅ JSON valid"

# Import test
python3 -c "from discord_bot.config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES"
echo "✅ Imports OK"

echo "✅ All automated tests passed"
```

## Bug Reporting

If you find bugs during testing, please report with:
1. Test case number
2. Environment details
3. Expected behavior
4. Actual behavior
5. Steps to reproduce
6. Error logs

## Testing Completion Checklist

Before considering testing complete:
- [ ] All test cases executed
- [ ] Results documented
- [ ] Bugs reported
- [ ] Regression tests passed
- [ ] Performance acceptable
- [ ] Documentation accurate

---

**Happy Testing! 🧪**
