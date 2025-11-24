"""Tests for test and script runner."""

import tempfile
from pathlib import Path
from src.repoman.runner import Runner


class TestRunner:
    """Test suite for Runner class."""

    def test_run_command_success(self):
        """Test running a successful command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(tmpdir)
            result = runner.run_command("echo 'Hello'")

            assert result["success"] is True
            assert result["returncode"] == 0
            assert "Hello" in result["stdout"]

    def test_run_command_failure(self):
        """Test running a failing command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(tmpdir)
            result = runner.run_command("exit 1")

            assert result["success"] is False
            assert result["returncode"] == 1

    def test_run_command_timeout(self):
        """Test command timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(tmpdir, timeout=1)
            result = runner.run_command("sleep 10", timeout=1)

            assert result["success"] is False
            assert "timed out" in result["stderr"].lower()

    def test_run_script_python(self):
        """Test running a Python script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "test_script.py"
            script_path.write_text("print('Script executed')")

            runner = Runner(tmpdir)
            result = runner.run_script(str(script_path))

            assert result["success"] is True
            assert "Script executed" in result["stdout"]

    def test_run_script_not_found(self):
        """Test running a non-existent script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(tmpdir)
            result = runner.run_script("nonexistent.py")

            assert result["success"] is False
            assert "not found" in result["stderr"].lower()

    def test_detect_test_command(self):
        """Test auto-detection of test command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = Runner(tmpdir)
            command = runner._detect_test_command()

            # Should default to pytest
            assert "pytest" in command.lower()
