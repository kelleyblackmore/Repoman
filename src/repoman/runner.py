"""Test and script runner for Repoman."""

import subprocess
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path


class Runner:
    """Handles running tests and scripts."""

    def __init__(self, repo_path: str, timeout: int = 300):
        """
        Initialize runner.

        Args:
            repo_path: Path to repository
            timeout: Default timeout in seconds
        """
        self.repo_path = Path(repo_path).resolve()
        self.timeout = timeout

    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Run a shell command.

        Args:
            command: Command to run
            cwd: Working directory (defaults to repo root)
            timeout: Timeout in seconds
            env: Environment variables

        Returns:
            Dictionary with returncode, stdout, stderr
        """
        work_dir = Path(cwd) if cwd else self.repo_path
        timeout = timeout or self.timeout

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                timeout=timeout,
                capture_output=True,
                text=True,
                env=env,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

    def run_tests(
        self,
        test_command: Optional[str] = None,
        test_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run tests.

        Args:
            test_command: Custom test command (auto-detects if None)
            test_path: Specific test file or directory

        Returns:
            Test results
        """
        if test_command is None:
            test_command = self._detect_test_command()

        if test_path:
            test_command = f"{test_command} {test_path}"

        result = self.run_command(test_command)
        result["test_command"] = test_command

        return result

    def _detect_test_command(self) -> str:
        """
        Auto-detect test command based on project structure.

        Returns:
            Test command string
        """
        # Check for common test frameworks
        if (self.repo_path / "pytest.ini").exists() or (
            self.repo_path / "setup.py"
        ).exists():
            return "pytest"
        elif (self.repo_path / "package.json").exists():
            return "npm test"
        elif (self.repo_path / "Makefile").exists():
            return "make test"
        elif (self.repo_path / "tox.ini").exists():
            return "tox"
        else:
            # Default to pytest for Python projects
            return "pytest"

    def run_linter(self, linter_command: Optional[str] = None) -> Dict[str, Any]:
        """
        Run linter.

        Args:
            linter_command: Custom linter command (auto-detects if None)

        Returns:
            Linter results
        """
        if linter_command is None:
            linter_command = self._detect_linter_command()

        result = self.run_command(linter_command)
        result["linter_command"] = linter_command

        return result

    def _detect_linter_command(self) -> str:
        """
        Auto-detect linter command based on project structure.

        Returns:
            Linter command string
        """
        # Check for Python linters
        if (self.repo_path / ".flake8").exists():
            return "flake8"
        elif (self.repo_path / "pylint.rc").exists():
            return "pylint"
        elif (self.repo_path / ".eslintrc.js").exists() or (
            self.repo_path / ".eslintrc.json"
        ).exists():
            return "eslint ."
        else:
            # Default to flake8 for Python projects
            return "flake8"

    def run_formatter(
        self, formatter_command: Optional[str] = None, check_only: bool = False
    ) -> Dict[str, Any]:
        """
        Run code formatter.

        Args:
            formatter_command: Custom formatter command
            check_only: Only check formatting without modifying files

        Returns:
            Formatter results
        """
        if formatter_command is None:
            formatter_command = self._detect_formatter_command(check_only)

        result = self.run_command(formatter_command)
        result["formatter_command"] = formatter_command

        return result

    def _detect_formatter_command(self, check_only: bool = False) -> str:
        """
        Auto-detect formatter command.

        Args:
            check_only: Only check formatting

        Returns:
            Formatter command string
        """
        # Check for Python formatters
        if (self.repo_path / "pyproject.toml").exists():
            if check_only:
                return "black --check ."
            else:
                return "black ."
        elif (self.repo_path / ".prettierrc").exists():
            if check_only:
                return "prettier --check ."
            else:
                return "prettier --write ."
        else:
            # Default to black for Python projects
            if check_only:
                return "black --check ."
            else:
                return "black ."

    def run_script(
        self, script_path: str, args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run a script file.

        Args:
            script_path: Path to script
            args: Script arguments

        Returns:
            Script execution results
        """
        script = Path(script_path)

        if not script.exists():
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Script not found: {script_path}",
            }

        # Build command based on file extension
        if script.suffix == ".py":
            command = f"{sys.executable} {script_path}"
        elif script.suffix == ".sh":
            command = f"bash {script_path}"
        elif script.suffix == ".js":
            command = f"node {script_path}"
        else:
            command = script_path

        if args:
            command += " " + " ".join(args)

        return self.run_command(command)
