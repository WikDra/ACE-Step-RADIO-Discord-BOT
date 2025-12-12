# Changelog

All notable changes to ACE-Step RADIO Discord BOT will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased - Beta Branch]

### Added
- **Linux Installer** (`setup.sh`): Full-featured installer for Linux with:
  - Automatic CUDA version detection (12.4 → 12.1 → 11.8 fallback)
  - Conda environment setup
  - FFmpeg detection and installation instructions
  - Colored console output
  - Error handling and validation
- **Multi-language Bot Interface**:
  - English language support for bot messages
  - `BOT_LANGUAGE` environment variable to switch between Polish and English
  - Bilingual message system maintaining backward compatibility
  - Easy extensibility for additional languages
- **Enhanced Music Presets**:
  - `lofi`: Lo-fi beats for studying
  - `metal`: Heavy metal music
  - `classical`: Classical orchestral music
  - `jazz`: Smooth jazz
  - `rock`: Classic rock
  - `sad`: Melancholic music
- **Complete Genre Support**:
  - Added missing genres: metal, funk, disco, punk, electronic
- **Complete Theme Support**:
  - Added missing themes: relaxing, calm, happy, instrumental
- **Comprehensive Documentation**:
  - `IMPROVEMENTS.md`: Detailed roadmap and suggestions
  - `CHANGELOG.md`: Version history and changes
  - Bilingual descriptions in presets

### Changed
- **README.md Improvements**:
  - Consolidated redundant system requirements sections
  - Improved GPU compatibility table with clearer information
  - Streamlined installation instructions for both Windows and Linux
  - Cleaned up troubleshooting section for better clarity
  - Removed duplicate content
  - Better organization and structure
- **Preset Descriptions**: All presets now have bilingual descriptions (English/Polish)
- **Environment Configuration**: Added `BOT_LANGUAGE` to `.env.example`

### Fixed
- Consistent CUDA version recommendations across documentation
- Installation instructions now clearly show both Windows and Linux paths

### Technical Improvements
- Modular message system allowing easy addition of new languages
- Backward compatible changes to constants module
- Better separation of concerns in configuration

## [Previous Versions]

### [1.0.0] - Initial Release
- Discord bot for real-time AI music generation
- ACE-Step integration
- Multi-language lyrics support (11 languages)
- Queue management system
- Music presets (party, chill, polish_pop, workout, romantic, focus)
- Windows installer (setup.bat)
- VRAM optimization modes
- Slash commands interface
- File upload functionality
- Bot statistics tracking

---

## Migration Notes

### Beta Branch Migration

If you're updating to the beta branch:

1. **Linux Users**: Use the new `setup.sh` installer
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Interface Language**: To use English interface, add to your `.env`:
   ```bash
   BOT_LANGUAGE=english
   ```

3. **New Presets**: Six new presets available (`lofi`, `metal`, `classical`, `jazz`, `rock`, `sad`)

4. **No Breaking Changes**: All existing functionality remains compatible

---

## Future Plans

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed roadmap and proposed features.

### Coming Soon
- Enhanced error handling with retry logic
- Performance monitoring dashboard
- User preferences system
- Additional language interfaces (Spanish, German, French, etc.)
- Web dashboard for bot management

### Under Consideration
- Plugin system for custom generators
- Social features (voting, leaderboards)
- Advanced audio effects
- Mobile app integration
- RESTful API

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project inherits the license from [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step).

## Acknowledgments

- **[ACE-Step Team](https://github.com/ace-step/ACE-Step)** - Original AI music generation model
- **[PasiKoodaa](https://github.com/PasiKoodaa/ACE-Step-RADIO)** - ACE-Step-RADIO base
- **[Discord.py](https://discordpy.readthedocs.io/)** - Discord API wrapper
- All contributors to the beta branch improvements
