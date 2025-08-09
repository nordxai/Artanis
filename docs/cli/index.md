# Artanis CLI

The Artanis Command Line Interface (CLI) helps you quickly scaffold new projects and manage your applications.

## Installation

The CLI is included when you install Artanis:

```bash
pip install artanis
```

Verify the installation:

```bash
artanis --version
```

## Available Commands

### `artanis new`

Creates a new Artanis project with a basic template.

**Usage:**
```bash
artanis new <project_name> [base_directory] [options]
```

**Arguments:**
- `project_name` - Name of the project to create (required)
- `base_directory` - Directory to create the project in (default: current directory)

**Options:**
- `--force, -f` - Overwrite existing files if they exist

**Examples:**

```bash
# Create a new project in the current directory
artanis new my-blog-api

# Create a project in a specific directory
artanis new my-api /path/to/projects

# Force overwrite existing files
artanis new my-api --force
```

## Generated Project Structure

When you create a new project, Artanis generates:

```
my-blog-api/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

### app.py

The main application file contains a minimal Artanis application:

```python
import uvicorn
from artanis import App

app = App()

async def root():
    return {"message": "Hello from my-blog-api!"}

app.get("/", root)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
```

### requirements.txt

Contains the minimal dependencies needed:

```txt
# Core dependencies for my-blog-api
artanis>=0.1.1
uvicorn[standard]

# Optional development dependencies (uncomment as needed)
# pytest>=7.0.0                    # For testing
# pytest-asyncio>=0.21.0           # Async testing support
# requests>=2.31.0                 # For API testing
# python-dotenv>=1.0.0             # Environment variable management
# pydantic>=2.0.0                  # Data validation and settings
```

### README.md

Comprehensive documentation for your new project including:

- Setup instructions
- How to run the application
- API endpoints documentation
- Development guidelines
- Troubleshooting tips

## Quick Start with CLI

Here's the fastest way to get a new Artanis project running:

```bash
# 1. Create the project
artanis new my-awesome-api

# 2. Navigate to the project directory
cd my-awesome-api

# 3. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

Your application will be running at `http://127.0.0.1:8000`!

## Project Name Validation

The CLI validates project names to ensure they're valid Python identifiers:

✅ **Valid names:**
- `my-blog-api`
- `user_management`
- `BlogAPI2024`
- `simple_app`

❌ **Invalid names:**
- `123-invalid` (starts with number)
- `my app` (contains spaces)
- `my@app` (contains special characters)
- Names longer than 50 characters

## Next Steps

After creating your project:

1. **Explore the generated code** - Understand the basic structure
2. **Add more routes** - Expand your API with additional endpoints
3. **Add middleware** - Implement authentication, logging, CORS
4. **Connect a database** - Integrate with your preferred database
5. **Write tests** - Add unit tests for your endpoints
6. **Deploy** - Deploy your application to production

## CLI Help

Get help for any command:

```bash
# General help
artanis --help

# Command-specific help
artanis new --help
```

## Troubleshooting

### Command not found

If you get `artanis: command not found`:

1. Make sure Artanis is installed: `pip install artanis`
2. Check your PATH includes pip's binary directory
3. Try using the full path: `python -m artanis.cli.main`

### Permission errors

If you get permission errors:

1. Use a virtual environment (recommended)
2. Use `--user` flag when installing: `pip install --user artanis`
3. Avoid using `sudo` with pip

### Project already exists

If the project directory already exists:

- Use `--force` to overwrite: `artanis new myproject --force`
- Or choose a different name/location

## Future CLI Features

Planned features for future releases:

- `artanis generate` - Generate specific components (routes, middleware)
- `artanis serve` - Development server with hot reloading
- `artanis test` - Run project tests
- `artanis deploy` - Deploy to various platforms
- Project templates - Different starter templates for common use cases

---

The CLI makes it easy to get started with Artanis quickly and consistently. For more advanced usage, see our [tutorial](../tutorials/index.md) and [examples](../examples/index.md).
