"""Implementation of the 'new' command."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from artanis._version import __version__


class NewCommand:
    """Command to create a new Artanis project."""

    def __init__(self) -> None:
        """Initialize the new command."""
        self.template_dir = Path(__file__).parent.parent / "templates" / "basic"

    def validate_project_name(self, name: str) -> None:
        """Validate the project name."""
        if not name:
            msg = "Project name cannot be empty"
            raise ValueError(msg)

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
            msg = "Project name must start with a letter and contain only letters, numbers, hyphens, and underscores"
            raise ValueError(msg)

        if len(name) > 50:
            msg = "Project name must be 50 characters or less"
            raise ValueError(msg)

    def create_project_directory(
        self, project_name: str, base_directory: str, force: bool
    ) -> Path:
        """Create the project directory."""
        base_path = Path(base_directory).resolve()
        project_path = base_path / project_name

        if project_path.exists():
            if not force:
                if project_path.is_dir() and any(project_path.iterdir()):
                    msg = f"Directory '{project_path}' already exists and is not empty. Use --force to overwrite."
                    raise ValueError(msg)
                if project_path.is_file():
                    msg = f"File '{project_path}' already exists. Use --force to overwrite."
                    raise ValueError(msg)
            # Remove existing directory/file if force is True
            elif project_path.is_dir():
                shutil.rmtree(project_path)
            else:
                project_path.unlink()

        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    def substitute_variables(self, content: str, project_name: str) -> str:
        """Substitute template variables in content."""
        replacements = {
            "{{project_name}}": project_name,
            "{{project_description}}": f"A new Artanis project named {project_name}",
            "{{artanis_version}}": __version__,
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        return content

    def copy_template_files(self, project_path: Path, project_name: str) -> None:
        """Copy template files to the project directory."""
        if not self.template_dir.exists():
            msg = f"Template directory not found: {self.template_dir}"
            raise FileNotFoundError(msg)

        for template_file in self.template_dir.rglob("*"):
            if template_file.is_file():
                # Calculate relative path from template dir
                relative_path = template_file.relative_to(self.template_dir)
                target_path = project_path / relative_path

                # Create parent directories if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Read template content and substitute variables
                try:
                    content = template_file.read_text(encoding="utf-8")
                    content = self.substitute_variables(content, project_name)
                    target_path.write_text(content, encoding="utf-8")
                except UnicodeDecodeError:
                    # For binary files, just copy without substitution
                    shutil.copy2(template_file, target_path)

    def create_virtual_environment(self, project_path: Path) -> None:
        """Create a virtual environment and install dependencies."""
        venv_path = project_path / "venv"

        try:
            # Create virtual environment
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            # Determine the correct pip path based on platform
            if os.name == "nt":  # Windows
                pip_path = venv_path / "Scripts" / "pip"
            else:  # Unix/Linux/macOS
                pip_path = venv_path / "bin" / "pip"

            # Install dependencies from requirements.txt
            requirements_path = project_path / "requirements.txt"
            if requirements_path.exists():
                subprocess.run(
                    [str(pip_path), "install", "-r", str(requirements_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )

        except subprocess.CalledProcessError as e:
            # Check if it's a common venv installation issue
            if "ensurepip" in str(e) or "python3-venv" in str(e):
                msg = (
                    "Virtual environment creation failed. On Ubuntu/Debian systems, "
                    "install python3-venv with: sudo apt install python3.8-venv"
                )
            else:
                msg = f"Failed to create virtual environment: {e}"
            raise RuntimeError(msg) from e
        except FileNotFoundError as e:
            msg = f"Python venv module not available: {e}. Please install Python with venv support."
            raise RuntimeError(msg) from e

    def display_success_message(
        self, project_name: str, project_path: Path, venv_created: bool = False
    ) -> None:
        """Display success message and next steps."""
        print(f"✅ Successfully created new Artanis project: {project_name}")
        print(f"📁 Project created at: {project_path}")

        if venv_created:
            venv_path = project_path / "venv"
            print(f"🐍 Virtual environment created: {venv_path}")
            print("📦 Dependencies installed")

        print()
        print("📋 Next steps:")
        print(f"   1. cd {project_name}")

        if venv_created:
            if os.name == "nt":  # Windows
                print("   2. venv\\Scripts\\activate")
            else:  # Unix/Linux/macOS
                print("   2. source venv/bin/activate")
            print("   2. pip install -r requirements.txt")
            print("   3. python app.py")

        print()
        print("🌐 Your server will be available at: http://127.0.0.1:8000")
        print("📚 Check the README.md file for more information.")

    def execute(
        self, project_name: str, base_directory: str, venv: bool, force: bool
    ) -> int:
        """Execute the new command."""
        try:
            # Validate project name
            self.validate_project_name(project_name)

            # Create project directory
            project_path = self.create_project_directory(
                project_name, base_directory, force
            )

            # Copy template files
            self.copy_template_files(project_path, project_name)

            # Create virtual environment if requested
            venv_created = False
            if venv:
                self.create_virtual_environment(project_path)
                venv_created = True

            # Display success message
            self.display_success_message(project_name, project_path, venv_created)

            return 0

        except (ValueError, FileNotFoundError, OSError, RuntimeError) as e:
            print(f"Error: {e}")
            return 1
