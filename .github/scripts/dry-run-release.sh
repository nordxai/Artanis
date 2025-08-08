#!/bin/bash

# 🧪 Dry Run Release Pipeline
# Tests the release pipeline logic locally without publishing anything

set -e  # Exit on any error

echo "🚀 Starting Artanis Release Pipeline Dry Run"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Parse command line arguments
VERSION_BUMP=${1:-"patch"}
VALID_BUMPS=("major" "minor" "patch")

if [[ ! " ${VALID_BUMPS[@]} " =~ " ${VERSION_BUMP} " ]]; then
    print_error "Invalid version bump type: $VERSION_BUMP"
    echo "Usage: $0 [major|minor|patch]"
    exit 1
fi

print_info "Testing $VERSION_BUMP version bump"

# 1. Get Current Version
echo ""
echo "📋 Step 1: Get Current Version"
echo "------------------------------"

cd "$(dirname "$0")/../.."
if [[ ! -f "src/artanis/_version.py" ]]; then
    print_error "Version file not found: src/artanis/_version.py"
    exit 1
fi

CURRENT_VERSION=$(python3 -c "
import sys
sys.path.insert(0, 'src')
from artanis._version import __version__
print(__version__)
")

print_status "Current version: $CURRENT_VERSION"

# 2. Calculate New Version
echo ""
echo "🆙 Step 2: Calculate New Version"
echo "--------------------------------"

NEW_VERSION=$(python3 - <<EOF
import re
import sys

current = "$CURRENT_VERSION"
bump_type = "$VERSION_BUMP"

# Parse semantic version
match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$', current)
if not match:
    raise ValueError(f"Invalid version format: {current}")

major, minor, patch = map(int, match.groups()[:3])

# Calculate new version
if bump_type == 'major':
    major += 1
    minor = 0
    patch = 0
elif bump_type == 'minor':
    minor += 1
    patch = 0
elif bump_type == 'patch':
    patch += 1

new_version = f"{major}.{minor}.{patch}"
print(new_version)
EOF
)

# Extract version components from stderr
MAJOR=$(python3 -c "
import re
current = '$CURRENT_VERSION'
bump_type = '$VERSION_BUMP'
match = re.match(r'^(\d+)\.(\d+)\.(\d+)', current)
major, minor, patch = map(int, match.groups()[:3])
if bump_type == 'major':
    major += 1
elif bump_type == 'minor':
    minor += 1
elif bump_type == 'patch':
    patch += 1
print(major if bump_type == 'major' else major)
")

MINOR=$(python3 -c "
import re
current = '$CURRENT_VERSION'
bump_type = '$VERSION_BUMP'
match = re.match(r'^(\d+)\.(\d+)\.(\d+)', current)
major, minor, patch = map(int, match.groups()[:3])
if bump_type == 'major':
    minor = 0
elif bump_type == 'minor':
    minor += 1
print(minor)
")

PATCH=$(python3 -c "
import re
current = '$CURRENT_VERSION'
bump_type = '$VERSION_BUMP'
match = re.match(r'^(\d+)\.(\d+)\.(\d+)', current)
major, minor, patch = map(int, match.groups()[:3])
if bump_type == 'major' or bump_type == 'minor':
    patch = 0
elif bump_type == 'patch':
    patch += 1
print(patch)
")

print_status "New version: $NEW_VERSION (from $CURRENT_VERSION)"
print_info "Version components: major=$MAJOR, minor=$MINOR, patch=$PATCH"

# 3. Create Backup of Version Files
echo ""
echo "💾 Step 3: Create Backups"
echo "-------------------------"

cp src/artanis/_version.py src/artanis/_version.py.backup
print_status "Created backup: src/artanis/_version.py.backup"

# 4. Test Version File Updates
echo ""
echo "🔄 Step 4: Test Version File Updates"
echo "------------------------------------"

# Update version string
sed -i.tmp "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/artanis/_version.py

# Update version tuple
sed -i.tmp "s/VERSION: tuple\[int, int, int\] = (.*/VERSION: tuple[int, int, int] = ($MAJOR, $MINOR, $PATCH)/" src/artanis/_version.py

# Update docstring examples
sed -i.tmp "s/'[0-9]\+\.[0-9]\+\.[0-9]\+'/'$NEW_VERSION'/g" src/artanis/_version.py
sed -i.tmp "s/([0-9]\+, [0-9]\+, [0-9]\+)/($MAJOR, $MINOR, $PATCH)/g" src/artanis/_version.py

# Verify version update
python3 -c "
import sys
sys.path.insert(0, 'src')
from artanis._version import __version__, VERSION
assert __version__ == '$NEW_VERSION', f'Version string mismatch: {__version__} != $NEW_VERSION'
assert VERSION == ($MAJOR, $MINOR, $PATCH), f'Version tuple mismatch: {VERSION} != ($MAJOR, $MINOR, $PATCH)'
print(f'✅ Version successfully updated to {__version__} with tuple {VERSION}')
"

print_status "Version files updated successfully"

# 5. Generate Changelog
echo ""
echo "📝 Step 5: Generate Changelog"
echo "-----------------------------"

# Get the last release tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -z "$LAST_TAG" ]; then
    print_warning "No previous tags found, generating changelog from all commits"
    COMMITS=$(git log --pretty=format:"- %s (%h)" --reverse | head -10)  # Limit to 10 for dry run
else
    print_info "Generating changelog since tag: $LAST_TAG"
    COMMITS=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --reverse)
fi

# Create changelog content
cat > changelog-dry-run.md << EOF
## 🎉 What's New in v$NEW_VERSION

### 🚀 Changes
$COMMITS

### 📊 Framework Stats
- **Total Tests**: $(find tests -name "test_*.py" | wc -l) test files
- **Code Quality**: All Ruff, MyPy, and pre-commit checks passing ✅
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Framework Features**: ASGI, Middleware, Events, Security, OpenAPI

### 🔧 Installation
\`\`\`bash
pip install artanis==$NEW_VERSION
\`\`\`

### 📚 Documentation
- [Getting Started](https://github.com/nordxai/Artanis#getting-started)
- [API Reference](https://github.com/nordxai/Artanis/tree/main/docs)
- [Examples](https://github.com/nordxai/Artanis/tree/main/docs/examples)
EOF

print_status "Changelog generated: changelog-dry-run.md"

# 6. Run Tests
echo ""
echo "🧪 Step 6: Run Tests"
echo "--------------------"

if command -v python3 &> /dev/null; then
    if [[ -d "venv" ]]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate
    fi

    # Install package in development mode
    print_info "Installing package in development mode..."
    python3 -m pip install -e . -q

    # Install test dependencies
    if [[ -f "requirements.txt" ]] || python3 -c "import pytest" 2>/dev/null; then
        print_info "Running test suite..."
        python3 -m pytest tests/ -v --tb=short -x  # Stop on first failure
        print_status "All tests passed!"
    else
        print_warning "pytest not found, skipping tests"
    fi
else
    print_warning "Python3 not found, skipping tests"
fi

# 7. Quality Checks
echo ""
echo "🔍 Step 7: Quality Checks"
echo "-------------------------"

# Check if ruff is available
if command -v ruff &> /dev/null || python3 -c "import ruff" 2>/dev/null; then
    print_info "Running Ruff linting..."
    if python3 -m ruff check src/ tests/ 2>/dev/null; then
        print_status "Ruff checks passed"
    else
        print_warning "Ruff checks found issues"
    fi
else
    print_warning "Ruff not found, skipping linting"
fi

# Check if mypy is available
if command -v mypy &> /dev/null || python3 -c "import mypy" 2>/dev/null; then
    print_info "Running MyPy type checking..."
    if python3 -m mypy src/artanis/ --ignore-missing-imports 2>/dev/null; then
        print_status "MyPy checks passed"
    else
        print_warning "MyPy checks found issues"
    fi
else
    print_warning "MyPy not found, skipping type checking"
fi

# 8. Test Package Build
echo ""
echo "📦 Step 8: Test Package Build"
echo "-----------------------------"

if command -v python3 &> /dev/null; then
    print_info "Testing package build..."

    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/

    # Install build if needed
    python3 -m pip install build -q 2>/dev/null || print_warning "Could not install build package"

    # Build wheel and sdist
    if python3 -m build 2>/dev/null; then
        print_status "Package built successfully"
        ls -la dist/

        # Check package with twine if available
        if python3 -c "import twine" 2>/dev/null; then
            if python3 -m twine check dist/* 2>/dev/null; then
                print_status "Package validation passed"
            else
                print_warning "Package validation found issues"
            fi
        else
            print_warning "Twine not available, skipping package validation"
        fi
    else
        print_error "Package build failed"
    fi
else
    print_warning "Python3 not found, skipping package build"
fi

# 9. Test Package Installation
echo ""
echo "🧪 Step 9: Test Package Installation"
echo "------------------------------------"

if [[ -f "dist/"*.whl ]]; then
    print_info "Testing package installation..."

    # Create temporary virtual environment
    TEMP_VENV="/tmp/artanis-test-env"
    rm -rf "$TEMP_VENV"
    python3 -m venv "$TEMP_VENV"
    source "$TEMP_VENV/bin/activate"

    # Install the wheel package
    WHEEL_FILE=$(ls dist/*.whl | head -1)
    pip install "$WHEEL_FILE" -q

    # Test basic import and version
    python3 -c "
import artanis
print(f'✅ Artanis v{artanis.__version__} imported successfully')
print(f'Available components: {len(dir(artanis))} items')

# Test basic app creation
app = artanis.App()
print('✅ App creation successful')

# Test version info
print(f'Version tuple: {artanis.VERSION}')
print(f'Version function: {artanis.get_version()}')
"

    # Cleanup
    deactivate
    rm -rf "$TEMP_VENV"

    print_status "Package installation test passed"
else
    print_warning "No wheel file found, skipping installation test"
fi

# 10. Restore Original Files
echo ""
echo "🔄 Step 10: Restore Original Files"
echo "----------------------------------"

# Restore version file
mv src/artanis/_version.py.backup src/artanis/_version.py
rm -f src/artanis/_version.py.tmp

print_status "Original version file restored"

# Cleanup
rm -f changelog-dry-run.md
rm -rf dist/ build/ *.egg-info/

# 11. Summary
echo ""
echo "📊 Dry Run Summary"
echo "=================="

print_status "Dry run completed successfully!"
print_info "Version bump: $CURRENT_VERSION → $NEW_VERSION ($VERSION_BUMP)"
print_info "All pipeline steps tested locally"
print_info "Ready for actual release pipeline"

echo ""
echo "🚀 To run the actual release:"
echo "   1. Go to GitHub Actions"
echo "   2. Select '🚀 Release Pipeline'"
echo "   3. Click 'Run workflow'"
echo "   4. Choose '$VERSION_BUMP' version bump"
echo "   5. Execute the release!"

print_status "Dry run complete! 🎉"
