# 🚀 Release Pipeline Setup Guide

This guide explains how to configure the automated release pipeline for Artanis.

## 📋 Prerequisites

### 1. PyPI Trusted Publishing Setup

The release pipeline uses PyPI's trusted publishing feature for secure, token-free publishing. You need to configure this on PyPI:

#### Step 1: Create PyPI Account (if needed)
- Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
- Create account and verify email

#### Step 2: Configure Trusted Publishing
1. **Go to PyPI Account Settings**:
   - Visit [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
   - Click "Add a new publisher"

2. **Fill in Publisher Details**:
   ```
   PyPI project name: artanis
   Owner: nordxai
   Repository name: Artanis
   Workflow filename: release.yml
   Environment name: release
   ```

3. **Save Configuration**
   - PyPI will now trust GitHub Actions from your repository to publish

#### Step 3: Create GitHub Environment
1. **Go to Repository Settings**:
   - Navigate to `Settings > Environments`
   - Click "New environment"
   - Name it: `release`

2. **Configure Environment Protection** (Optional but Recommended):
   - **Required reviewers**: Add yourself or trusted maintainers
   - **Wait timer**: Set to 5 minutes for safety
   - **Deployment branches**: Restrict to `main` branch only

### 2. GitHub Permissions

The workflow uses these GitHub permissions (already configured in the workflow):
- `contents: write` - To create releases and tags
- `id-token: write` - For PyPI trusted publishing

## 🎯 How to Use the Release Pipeline

### Manual Release Trigger

1. **Go to GitHub Actions**:
   - Visit your repository on GitHub
   - Navigate to `Actions` tab
   - Select "🚀 Release Pipeline" workflow

2. **Click "Run workflow"**:
   - Choose branch: `main`
   - Select version bump type:
     - `patch` - Bug fixes (1.0.0 → 1.0.1)
     - `minor` - New features (1.0.0 → 1.1.0)
     - `major` - Breaking changes (1.0.0 → 2.0.0)
   - Check "Mark as pre-release" if needed
   - Check "Skip PyPI publishing" to only create GitHub release

3. **Confirm and Run**:
   - Review your selections
   - Click "Run workflow"

### What the Pipeline Does

#### 🏗️ Preparation Phase:
1. **Version Calculation**: Automatically calculates new version based on current version
2. **Changelog Generation**: Creates changelog from git commits since last release
3. **Version Updates**: Updates `src/artanis/_version.py` with new version
4. **Quality Assurance**: Runs all tests and quality checks (Ruff, MyPy)
5. **Package Building**: Creates wheel and source distributions

#### 🧪 Testing Phase:
- **Multi-Python Testing**: Tests package installation on Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Import Verification**: Ensures package imports correctly on all versions
- **Basic Functionality**: Tests core Artanis functionality

#### 📦 Publishing Phase:
- **PyPI Release**: Publishes to PyPI using trusted publishing (if enabled)
- **GitHub Release**: Creates GitHub release with changelog and assets
- **Git Tagging**: Creates and pushes version tag

#### 🎉 Notification Phase:
- **Success Summary**: Shows release details and installation commands
- **Failure Alerts**: Provides detailed error information if something fails

## 🔧 Pipeline Features

### Automatic Version Management
```python
# Before release (current version)
__version__ = "0.2.1"

# After patch release
__version__ = "0.2.2"

# After minor release
__version__ = "0.3.0"

# After major release
__version__ = "1.0.0"
```

### Changelog Generation
The pipeline automatically generates changelogs from git commits:

```markdown
## 🎉 What's New in v0.2.2

### 🚀 Changes
- Fix middleware chain execution bug (a1b2c3d)
- Add OpenAPI validation middleware (e4f5g6h)
- Update security headers configuration (i7j8k9l)

### 📊 Framework Stats
- **Total Tests**: 7 test files
- **Code Quality**: All Ruff, MyPy, and pre-commit checks passing ✅
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Framework Features**: ASGI, Middleware, Events, Security, OpenAPI
```

### Release Assets
Each release includes:
- **Wheel file**: `artanis-X.Y.Z-py3-none-any.whl`
- **Source distribution**: `artanis-X.Y.Z.tar.gz`
- **Changelog**: Detailed release notes
- **Installation instructions**: Ready-to-use pip commands

## 🛡️ Safety Features

### Multi-Stage Validation
- **Pre-release Testing**: All tests must pass before building
- **Multi-Python Compatibility**: Tests on 5 Python versions
- **Package Verification**: Validates package structure with `twine check`
- **Import Testing**: Verifies imports work on all Python versions

### Environment Protection
- **Release Environment**: Optional approval process before publishing
- **Branch Restrictions**: Only runs from main branch
- **Pre-release Marking**: Option to mark releases as pre-release

### Error Handling
- **Graceful Failures**: Pipeline stops if any stage fails
- **Detailed Logging**: Comprehensive logs for debugging
- **Rollback Safety**: Version commits only happen after successful tests

## 📊 Example Release Flow

### Starting a Patch Release:
```bash
# Current state
git tag --list  # shows: v0.2.1
cat src/artanis/_version.py  # shows: __version__ = "0.2.1"
```

### After Pipeline Runs:
```bash
# New state
git tag --list  # shows: v0.2.1, v0.2.2
cat src/artanis/_version.py  # shows: __version__ = "0.2.2"

# PyPI updated
pip install artanis==0.2.2  # ✅ Works!

# GitHub release created
# Visit: https://github.com/nordxai/Artanis/releases/tag/v0.2.2
```

## 🚨 Troubleshooting

### Common Issues:

#### PyPI Publishing Fails
- **Check trusted publishing**: Verify PyPI configuration matches GitHub repo
- **Environment setup**: Ensure `release` environment exists in GitHub
- **Repository name**: Must match exactly (case-sensitive)

#### Tests Fail During Release
- **Run locally first**: `pytest tests/ -v` to catch issues early
- **Check quality tools**: `ruff check src/ tests/` and `mypy src/artanis/`
- **Version conflicts**: Ensure no uncommitted changes in version files

#### Version Calculation Errors
- **Check current version**: Must be valid semver (X.Y.Z format)
- **Clean git state**: Commit all changes before running pipeline
- **Branch selection**: Must run from main branch

### Getting Help
- **Pipeline Logs**: Check GitHub Actions logs for detailed error messages
- **Test Locally**: Run `python -m build` and `twine check dist/*` locally
- **PyPI Status**: Check [https://status.python.org/](https://status.python.org/) for outages

## 🎯 Best Practices

### Before Releasing:
1. **Test thoroughly**: Run full test suite locally
2. **Update documentation**: Ensure README and docs are current
3. **Check dependencies**: Verify all dependencies are properly specified
4. **Review changes**: Check git log since last release

### Release Strategy:
- **Patch releases**: Bug fixes, security updates, documentation improvements
- **Minor releases**: New features, non-breaking API additions
- **Major releases**: Breaking changes, major architecture updates

### After Releasing:
1. **Verify installation**: Test `pip install artanis==X.Y.Z` works
2. **Check documentation**: Ensure release notes are accurate
3. **Monitor issues**: Watch for user reports of problems
4. **Update examples**: Ensure examples work with new version

## 🔄 Manual Backup Process

If the automated pipeline fails, you can release manually:

```bash
# 1. Update version
vim src/artanis/_version.py

# 2. Run tests
pytest tests/ -v

# 3. Build package
python -m build

# 4. Check package
twine check dist/*

# 5. Upload to PyPI (with API token)
twine upload dist/*

# 6. Create GitHub release manually
gh release create v1.0.0 dist/* --title "Release v1.0.0" --notes-file changelog.md
```

This automated release pipeline ensures consistent, safe, and comprehensive releases for the Artanis framework.
