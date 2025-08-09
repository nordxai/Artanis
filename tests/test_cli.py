"""Tests for the Artanis CLI."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from artanis.cli.commands.new import NewCommand
from artanis.cli.main import create_parser, main


class TestCLIParser:
    """Test CLI argument parsing."""

    def test_parser_help(self):
        """Test parser shows help when no command is provided."""
        parser = create_parser()
        assert parser.prog == "artanis"

    def test_new_command_parser(self):
        """Test new command argument parsing."""
        parser = create_parser()

        # Test with project name only
        args = parser.parse_args(["new", "test-project"])
        assert args.command == "new"
        assert args.project_name == "test-project"
        assert args.base_directory == "."
        assert args.venv is False
        assert args.force is False

        # Test with base directory
        args = parser.parse_args(["new", "my-app", "/tmp"])
        assert args.command == "new"
        assert args.project_name == "my-app"
        assert args.base_directory == "/tmp"
        assert args.venv is False
        assert args.force is False

        # Test with all options
        args = parser.parse_args(["new", "my-app", "/tmp", "--venv", "--force"])
        assert args.command == "new"
        assert args.project_name == "my-app"
        assert args.base_directory == "/tmp"
        assert args.venv is True
        assert args.force is True


class TestNewCommand:
    """Test the new command functionality."""

    def test_validate_project_name_valid(self):
        """Test valid project names."""
        command = NewCommand()

        # These should not raise exceptions
        command.validate_project_name("test-project")
        command.validate_project_name("my_app")
        command.validate_project_name("app123")
        command.validate_project_name("BlogAPI")

    def test_validate_project_name_invalid(self):
        """Test invalid project names."""
        command = NewCommand()

        # Empty name
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            command.validate_project_name("")

        # Starts with number
        with pytest.raises(ValueError, match="must start with a letter"):
            command.validate_project_name("123app")

        # Contains spaces
        with pytest.raises(ValueError, match="must start with a letter"):
            command.validate_project_name("my app")

        # Contains special characters
        with pytest.raises(ValueError, match="must start with a letter"):
            command.validate_project_name("my@app")

        # Too long
        with pytest.raises(ValueError, match="must be 50 characters or less"):
            command.validate_project_name("a" * 51)

    def test_substitute_variables(self):
        """Test template variable substitution."""
        command = NewCommand()

        content = "Project: {{project_name}}, Description: {{project_description}}"
        result = command.substitute_variables(content, "test-app")

        assert "test-app" in result
        assert "A new Artanis project named test-app" in result
        assert "{{" not in result  # All variables should be substituted

    def test_create_project_success(self):
        """Test successful project creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = NewCommand()

            # Mock template directory to avoid file system dependencies
            with patch.object(command, "template_dir") as mock_template_dir:
                mock_template_dir.exists.return_value = True
                mock_template_dir.rglob.return_value = []  # No template files

                with patch.object(command, "copy_template_files"):
                    with patch.object(command, "display_success_message"):
                        result = command.execute("test-project", temp_dir, False, False)

                        assert result == 0
                        project_path = Path(temp_dir) / "test-project"
                        assert project_path.exists()

    def test_create_project_existing_directory_no_force(self):
        """Test project creation fails when directory exists without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = NewCommand()

            # Create existing directory with a file
            project_dir = Path(temp_dir) / "existing-project"
            project_dir.mkdir()
            (project_dir / "existing_file.txt").write_text("test")

            result = command.execute("existing-project", temp_dir, False, False)
            assert result == 1

    def test_create_project_existing_directory_with_force(self):
        """Test project creation succeeds when directory exists with force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = NewCommand()

            # Create existing directory with a file
            project_dir = Path(temp_dir) / "existing-project"
            project_dir.mkdir()
            (project_dir / "existing_file.txt").write_text("test")

            # Mock template directory to avoid file system dependencies
            with patch.object(command, "template_dir") as mock_template_dir:
                mock_template_dir.exists.return_value = True
                mock_template_dir.rglob.return_value = []  # No template files

                with patch.object(command, "copy_template_files"):
                    with patch.object(command, "display_success_message"):
                        result = command.execute(
                            "existing-project", temp_dir, False, True
                        )

                        assert result == 0
                        assert project_dir.exists()
                        # Original file should be gone due to force flag
                        assert not (project_dir / "existing_file.txt").exists()

    def test_virtual_environment_creation(self):
        """Test virtual environment creation with --venv flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = NewCommand()

            # Mock template directory and subprocess calls
            with patch.object(command, "template_dir") as mock_template_dir:
                mock_template_dir.exists.return_value = True
                mock_template_dir.rglob.return_value = []

                with patch.object(command, "copy_template_files"):
                    with patch("subprocess.run") as mock_subprocess:
                        with patch.object(command, "display_success_message"):
                            mock_subprocess.return_value = (
                                None  # Successful subprocess call
                            )

                            result = command.execute(
                                "test-project", temp_dir, True, False
                            )

                            assert result == 0
                            # Verify subprocess was called for venv creation
                            assert mock_subprocess.call_count >= 1

    def test_virtual_environment_creation_failure(self):
        """Test virtual environment creation failure handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = NewCommand()

            # Mock template directory and subprocess calls
            with patch.object(command, "template_dir") as mock_template_dir:
                mock_template_dir.exists.return_value = True
                mock_template_dir.rglob.return_value = []

                with patch.object(command, "copy_template_files"):
                    with patch("subprocess.run") as mock_subprocess:
                        mock_subprocess.side_effect = subprocess.CalledProcessError(
                            1, "venv"
                        )

                        result = command.execute("test-project", temp_dir, True, False)

                        assert result == 1  # Should fail


class TestCLIMain:
    """Test main CLI entry point."""

    def test_main_no_command(self):
        """Test main function with no command shows help."""
        with patch("builtins.print") as mock_print:
            result = main([])
            assert result == 1

    def test_main_invalid_command(self):
        """Test main function with invalid command."""
        with pytest.raises(SystemExit):
            main(["invalid"])

    def test_main_new_command_success(self):
        """Test main function with new command actually creates project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = main(["new", "test-project", temp_dir])
            assert result == 0

            # Verify project was created
            project_path = Path(temp_dir) / "test-project"
            assert project_path.exists()
            assert (project_path / "app.py").exists()
            assert (project_path / "requirements.txt").exists()
            assert (project_path / "README.md").exists()

    def test_main_exception_handling(self):
        """Test main function handles exceptions."""
        # Test with invalid project name to trigger an exception
        with tempfile.TemporaryDirectory() as temp_dir:
            result = main(["new", "123invalid", temp_dir])
            assert result == 1

    def test_main_with_venv_flag(self):
        """Test main function with --venv flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("subprocess.run") as mock_subprocess:
                mock_subprocess.return_value = None  # Successful subprocess call

                result = main(["new", "test-project", temp_dir, "--venv"])
                assert result == 0

                # Verify project was created
                project_path = Path(temp_dir) / "test-project"
                assert project_path.exists()
                assert (project_path / "app.py").exists()

    def test_main_with_dot_directory(self):
        """Test main function with current directory specified as '.'."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory and run with "."
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = main(["new", "test-project", "."])
                assert result == 0

                # Verify project was created in current directory
                project_path = Path(temp_dir) / "test-project"
                assert project_path.exists()
                assert (project_path / "app.py").exists()
            finally:
                os.chdir(original_cwd)
