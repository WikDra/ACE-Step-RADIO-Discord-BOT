# Branch Structure

This document describes the branch structure for the ACE-Step RADIO Discord BOT repository.

## Branches

### `beta` (Branch created: 2024-12-12)
- **Purpose**: Beta branch with all new features and improvements
- **Base**: Contains all changes from the cleanup-readme-and-add-linux-installer work
- **Commit**: 77fe968
- **Status**: Ready for testing and user feedback

**Features:**
- Linux installer (setup.sh)
- English language interface support
- 6 new music presets
- Enhanced documentation
- Security improvements

### `release/1dev` (Branch created: 2024-12-12)
- **Purpose**: Development release branch, copy of main/baseline
- **Base**: e8ecbcc (base commit before beta changes)
- **Status**: Stable baseline

## Branch Creation

```bash
# Beta branch was created with all improvements:
git branch beta 77fe968

# Release/1dev was created from the base:
git branch release/1dev e8ecbcc
```

## Pushing Branches

**Note**: Branches have been created locally. To make them visible on GitHub, they need to be pushed:

```bash
# Push beta branch
git push -u origin beta

# Push release/1dev branch
git push -u origin release/1dev
```

## Current Branch Structure

```
e8ecbcc (release/1dev) - Base commit
  |
  +-- 90d8cf9 - Initial plan
  +-- 9ad62cd - Add cleaned README, Linux installer, and English interface support
  +-- ac9fbb0 - Add comprehensive improvements
  +-- a4969d3 - Add comprehensive testing guide
  +-- c3048b7 - Address code review: security improvements
  +-- 895c056 - Final improvements: CPU fallback, language warning
  +-- 77fe968 (beta) - Final beta summary and complete testing validation
```
