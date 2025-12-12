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

## How to Create Branches Locally

Since the branches cannot be pushed from the CI environment, you need to create them locally from the PR commits:

```bash
# First, fetch the PR branch
git fetch origin copilot/cleanup-readme-and-add-linux-installer

# Create beta branch from commit 77fe968
git branch beta 77fe968

# Create release/1dev branch from commit e8ecbcc  
git branch release/1dev e8ecbcc

# Push both branches to make them visible on GitHub
git push -u origin beta
git push -u origin release/1dev
```

**Alternative - Create from the fetched branch:**

```bash
# Fetch the PR
git fetch origin copilot/cleanup-readme-and-add-linux-installer:copilot-pr

# Create beta from specific commit in the PR
git branch beta copilot-pr~1  # This points to commit 77fe968

# Create release/1dev from the base
git branch release/1dev e8ecbcc

# Push both branches
git push -u origin beta
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
