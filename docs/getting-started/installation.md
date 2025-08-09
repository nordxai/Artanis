# Installation

This guide will walk you through installing Artanis and setting up your development environment.

## Requirements

Before installing Artanis, ensure you have:

- **Python 3.8+** - Artanis supports Python 3.8, 3.9, 3.10, 3.11, and 3.13
- **pip** - Python package manager (usually comes with Python)
- **venv** (recommended) - For creating isolated Python environments

!!! tip "Check Your Python Version"
    ```bash
    python --version
    # or
    python3 --version
    ```

## Install from PyPI

The easiest way to install Artanis is using pip:

```bash
pip install artanis
```

This installs the latest stable version of Artanis with zero runtime dependencies.

## Development Installation

If you want to contribute to Artanis or need the latest development features:

### Clone the Repository

```bash
git clone https://github.com/nordxai/Artanis
cd Artanis
```

### Create Virtual Environment

=== "Linux/macOS"
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

=== "Windows"
    ```cmd
    python -m venv venv
    venv\Scripts\activate
    ```

### Install in Development Mode

```bash
# Install with all development dependencies
pip install -e ".[dev]"

# Or install specific dependency groups
pip install -e ".[test]"     # Testing dependencies only
pip install -e ".[all]"      # All optional dependencies
```

## Verify Installation

Create a simple test to verify Artanis is installed correctly:

```python title="test_install.py"
from artanis import App
import artanis

print(f"Artanis version: {artanis.__version__}")

app = App()

async def hello():
    return {"message": "Artanis is working!"}

app.get("/", hello)

print("✅ Artanis installed successfully!")
```

Run the test:

```bash
python test_install.py
```

You should see output like:
```
Artanis version: 0.1.1
✅ Artanis installed successfully!
```

## Optional Dependencies

Artanis has zero runtime dependencies, but you may want to install additional packages for development:

### ASGI Server (Required for Running Apps)

```bash
# Uvicorn (recommended)
pip install uvicorn[standard]

# Or Hypercorn
pip install hypercorn
```

### Development Tools

```bash
# Code quality tools (included in [dev] group)
pip install ruff mypy pre-commit

# Testing tools (included in [test] group)
pip install pytest pytest-asyncio pytest-cov

# Documentation tools
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Database Drivers (for tutorials and examples)

```bash
# For SQLite (built into Python)
# No additional installation needed

# For PostgreSQL
pip install asyncpg

# For MySQL
pip install aiomysql
```

## Available Dependency Groups

When installing in development mode, you can use these dependency groups:

| Group | Description | Installation |
|-------|-------------|--------------|
| `dev` | Development tools (ruff, mypy, pre-commit, pytest) | `pip install -e ".[dev]"` |
| `test` | Testing and coverage tools | `pip install -e ".[test]"` |
| `all` | All optional dependencies | `pip install -e ".[all]"` |

## Installation Troubleshooting

### Common Issues

!!! warning "Python Version"
    Make sure you're using Python 3.8 or higher:
    ```bash
    python --version
    ```
    If you see Python 2.x, try using `python3` instead of `python`.

!!! warning "Virtual Environment"
    Always use a virtual environment to avoid dependency conflicts:
    ```bash
    python -m venv myproject-env
    source myproject-env/bin/activate  # Linux/macOS
    # or
    myproject-env\Scripts\activate     # Windows
    ```

!!! warning "Permission Errors"
    If you get permission errors, avoid using `sudo`. Instead:
    - Use a virtual environment (recommended)
    - Use the `--user` flag: `pip install --user artanis`

### Platform-Specific Notes

=== "Ubuntu/Debian"
    ```bash
    # Install Python 3.8+ if needed
    sudo apt update
    sudo apt install python3.8 python3.8-venv python3.8-pip

    # Create virtual environment
    python3.8 -m venv venv
    source venv/bin/activate
    pip install artanis
    ```

=== "CentOS/RHEL"
    ```bash
    # Install Python 3.8+ if needed
    sudo yum install python38 python38-pip

    # Create virtual environment
    python3.8 -m venv venv
    source venv/bin/activate
    pip install artanis
    ```

=== "macOS"
    ```bash
    # Using Homebrew (recommended)
    brew install python@3.8

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    pip install artanis
    ```

=== "Windows"
    1. Download Python from [python.org](https://python.org)
    2. Make sure to check "Add Python to PATH" during installation
    3. Open Command Prompt or PowerShell:
    ```cmd
    python -m venv venv
    venv\Scripts\activate
    pip install artanis
    ```

## Next Steps

Now that you have Artanis installed, you're ready to:

1. **[Create your first application](quickstart.md)** - Build a simple "Hello World" app
2. **[Follow the tutorial](../tutorials/index.md)** - Build a complete blog API step-by-step
3. **[Explore examples](../examples/index.md)** - See working code for common patterns

## Getting Help

If you encounter issues during installation:

1. Check our [troubleshooting guide](../contributing/development.md#troubleshooting)
2. Search [existing issues](https://github.com/nordxai/Artanis/issues) on GitHub
3. Create a [new issue](https://github.com/nordxai/Artanis/issues/new) with:
   - Your operating system and version
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce the problem
