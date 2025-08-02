# Contributing to Artanis

First off, thank you for considering contributing to Artanis! It's people like you that make Artanis such a great tool.

## Where do I go from here?

If you've noticed a bug or have a question, [search the issue tracker](https://github.com/nordxai/projectArtanis/issues) to see if someone else has already created a ticket. If not, feel free to [create a new issue](https://github.com/nordxai/projectArtanis/issues/new).

## Fork & create a branch

If you're looking to contribute code, the first step is to fork this repository and create a new branch from `main`. A good branch name would be `(fix|feat|docs)/<short-description-of-change>` (e.g., `fix/middleware-bug`, `feat/new-router-feature`, `docs/readme-update`).

## Get the code

```bash
# Clone your fork of the repository
git clone https://github.com/<your-username>/projectArtanis.git
cd projectArtanis

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Running Tests

To ensure that your changes don't break any existing functionality, please run the test suite:

```bash
pytest
```

If you're adding a new feature, please include tests for it.

## Code Style

Artanis uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Before committing your changes, please run:

```bash
ruff check --fix .
ruff format .
```

We also use [MyPy](http://mypy-lang.org/) for static type checking. Please run the following command to ensure your changes are type-safe:

```bash
- mypy src/artanis --strict --ignore-missing-imports
```

## Submitting a pull request

When you're ready to submit a pull request, please make sure to:

-   Write a clear and concise title and description.
-   Reference any related issues.
-   Ensure that all tests pass.
-   Ensure that the code is properly formatted and linted.

Thank you for your contribution!
