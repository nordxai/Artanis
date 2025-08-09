# Contributing to Documentation

This guide explains how to work with Artanis documentation, including local development, building, and deployment.

## Documentation Structure

The Artanis documentation is built with [MkDocs](https://www.mkdocs.org/) using the [Material theme](https://squidfunk.github.io/mkdocs-material/):

```
docs/
├── mkdocs.yml              # MkDocs configuration
├── .mkdocsignore          # Files to ignore during build
├── index.md               # Homepage
├── getting-started/       # Installation and tutorials
├── tutorials/             # Step-by-step guides
├── examples/              # Working code examples
├── api/                   # API reference (auto-generated)
├── cli/                   # CLI documentation
└── assets/                # Images and static files
```

## Prerequisites

Before working with the documentation, ensure you have:

1. **Python 3.8+** installed
2. **Artanis development environment** set up
3. **Documentation dependencies** installed:

```bash
# Install MkDocs and extensions
pip install mkdocs-material[recommended]
pip install mkdocstrings[python]
pip install ruff  # Required for API documentation formatting
```

## Local Development

### Starting the Development Server

To work on documentation locally with hot-reloading:

```bash
# Navigate to project root
cd /path/to/Artanis

# Start the development server
mkdocs serve --dev-addr 127.0.0.1:8080

# Or use the default port 8000
mkdocs serve
```

The documentation will be available at:
- **Custom port**: http://127.0.0.1:8080/Artanis/
- **Default port**: http://127.0.0.1:8000/

### Making Changes

1. **Edit markdown files** in the `docs/` directory
2. **Save changes** - the server will automatically reload
3. **View updates** in your browser immediately

### Adding New Pages

1. **Create the markdown file** in the appropriate directory
2. **Add to navigation** in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Your New Page: getting-started/new-page.md  # Add here
```

## Building Documentation

### Development Build

For testing purposes:

```bash
# Build documentation (allows warnings)
mkdocs build

# Build to custom directory
mkdocs build --site-dir /path/to/output
```

### Production Build

For deployment (strict mode):

```bash
# Build with strict validation (fails on warnings)
mkdocs build --strict

# Clean build (removes previous build first)
mkdocs build --clean --strict
```

### Troubleshooting Builds

Common build issues and solutions:

#### Missing Dependencies
```bash
# Error: ModuleNotFoundError: No module named 'material.extensions.emoji'
pip install mkdocs-material[recommended]

# Error: No module named 'mkdocstrings'
pip install mkdocstrings[python]

# Error: ruff not found (for API docs)
pip install ruff
```

#### Icon Issues
If Material Design icons show as raw text (`:material-icon:`):
- Ensure `pymdownx.emoji` extension is configured in `mkdocs.yml`
- Check that `mkdocs-material-extensions` is installed

#### Build Warnings
```bash
# File conflicts (README.md vs index.md)
# Remove conflicting files or add to .mkdocsignore

# Broken internal links
# Fix relative paths in markdown files

# Missing pages in navigation
# Add to mkdocs.yml nav section or ignore warning
```

## API Documentation

The API documentation is automatically generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

### Adding API Documentation

Create a new markdown file in `docs/api/`:

```markdown
# My Module

::: artanis.my_module.MyClass
    options:
      show_source: true
      show_signature_annotations: true
```

### API Documentation Options

Configure in `mkdocs.yml`:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_signature_annotations: true
```

## Deployment

### Automatic Deployment (GitHub Actions)

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

**Workflow**: `.github/workflows/docs.yml`
- Builds documentation with `mkdocs build --strict`
- Deploys to GitHub Pages
- Available at: https://nordxai.github.io/Artanis/

### Manual Deployment

For manual deployment to GitHub Pages:

```bash
# Deploy to GitHub Pages (requires git remote)
mkdocs gh-deploy

# Deploy with custom commit message
mkdocs gh-deploy --message "Update documentation"
```

### Custom Deployment

To deploy to other platforms:

```bash
# Build static site
mkdocs build

# Upload contents of site/ directory to your host
# The site/ directory contains the complete static website
```

## Configuration

### MkDocs Configuration (`mkdocs.yml`)

Key configuration sections:

```yaml
site_name: Artanis Framework
site_url: https://nordxai.github.io/Artanis
repo_url: https://github.com/nordxai/Artanis

theme:
  name: material
  features:
    - navigation.tabs        # Top-level navigation tabs
    - search.highlight      # Highlight search terms
    - content.code.copy     # Code copy buttons

plugins:
  - search                  # Built-in search
  - mkdocstrings:          # API documentation
      handlers:
        python:
          options:
            docstring_style: google

markdown_extensions:
  - pymdownx.emoji:         # Material Design icons
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - admonition              # Note/warning boxes
  - pymdownx.superfences    # Code blocks
  - attr_list               # HTML attributes in markdown
```

### Ignoring Files (`.mkdocsignore`)

Exclude files from documentation builds:

```
# Virtual environments
**/venv/
**/env/

# Python cache
**/__pycache__/
**/*.pyc

# IDE files
**/.vscode/
**/.idea/

# Backup files
**/*.bak
```

## Writing Guidelines

### Markdown Best Practices

1. **Use descriptive headings** (H1, H2, H3)
2. **Add code examples** with syntax highlighting
3. **Include internal links** to related sections
4. **Use admonitions** for important information

```markdown
!!! tip "Pro Tip"
    Use admonitions to highlight important information!

!!! warning "Important"
    Always test code examples before documenting them.
```

### Code Examples

Include working, tested code examples:

```python
from artanis import App

app = App()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}
```

### API Documentation Style

Use Google-style docstrings for consistency:

```python
def my_function(param1: str, param2: int = 0) -> dict:
    """Summary of the function.

    Longer description explaining the function's purpose and behavior.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to 0.

    Returns:
        Dictionary containing the result.

    Raises:
        ValueError: If param1 is empty.

    Examples:
        >>> my_function("hello", 42)
        {"result": "processed"}
    """
```

## Testing Documentation

### Content Testing

1. **Verify all links work** (internal and external)
2. **Test all code examples** by running them
3. **Check cross-references** between sections
4. **Validate markup rendering** in the browser

### Build Testing

```bash
# Test strict build (should pass for production)
mkdocs build --strict

# Test different Python versions (if applicable)
python3.8 -m mkdocs build --strict
python3.11 -m mkdocs build --strict
```

## Common Tasks

### Adding a New Example

1. **Create example directory**: `docs/examples/my-example/`
2. **Add working code**: `docs/examples/my-example/app.py`
3. **Write documentation**: `docs/examples/my-example.md`
4. **Add to navigation**: Update `mkdocs.yml`
5. **Test thoroughly**: Ensure all code works

### Updating API Documentation

1. **Update docstrings** in source code
2. **Rebuild documentation**: `mkdocs build`
3. **Verify auto-generated content** looks correct

### Adding Icons

Use Material Design icons in documentation:

```markdown
:material-rocket-launch: Quick Start
:octicons-arrow-right-24: Continue
:fontawesome-brands-github: Source Code
```

## Getting Help

If you encounter issues with documentation:

1. **Check the build output** for specific error messages
2. **Review the MkDocs logs** for warnings and errors
3. **Test with a clean build**: `mkdocs build --clean`
4. **Search existing issues** in the repository
5. **Create a new issue** with:
   - Your operating system
   - Python version
   - Installed packages (`pip list`)
   - Complete error message
   - Steps to reproduce

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme Docs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Python Docstring Conventions (PEP 257)](https://peps.python.org/pep-0257/)
