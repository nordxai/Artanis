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

    def display_success_message(self, project_name: str, project_path: Path) -> None:
        """Display success message and next steps."""
        print(f"✅ Successfully created new Artanis project: {project_name}")
        print(f"📁 Project created at: {project_path}")

        print()
        print("📋 Next steps:")
        print(f"   1. cd {project_name}")
        print("   2. pip install -r requirements.txt")
        print("   3. python app.py")

        print()
        print("🌐 Your server will be available at: http://127.0.0.1:8000")
        print("📚 Check the README.md file for more information.")

    def execute(self, project_name: str, base_directory: str, force: bool) -> int:
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

            # Display success message
            self.display_success_message(project_name, project_path)

            return 0

        except (ValueError, FileNotFoundError, OSError, RuntimeError) as e:
            print(f"Error: {e}")
            return 1
