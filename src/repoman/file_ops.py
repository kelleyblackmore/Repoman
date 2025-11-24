"""File operations for Repoman."""

import fnmatch
from pathlib import Path
from typing import List, Optional, Dict, Any


class FileOperations:
    """Handles file system operations for the autonomous agent."""

    def __init__(self, repo_path: str, protected_patterns: Optional[List[str]] = None):
        """
        Initialize file operations.

        Args:
            repo_path: Path to repository root
            protected_patterns: List of glob patterns for protected files
        """
        self.repo_path = Path(repo_path).resolve()
        self.protected_patterns = protected_patterns or [
            ".git/**",
            ".github/**",
            "config/**",
        ]

    def is_protected(self, file_path: str) -> bool:
        """
        Check if a file is protected from modifications.

        Args:
            file_path: Relative or absolute path to file

        Returns:
            True if file is protected
        """
        path = Path(file_path)
        if path.is_absolute():
            try:
                relative_path = path.relative_to(self.repo_path)
            except ValueError:
                return True  # Outside repo is protected
        else:
            relative_path = path

        relative_str = str(relative_path)

        for pattern in self.protected_patterns:
            if fnmatch.fnmatch(relative_str, pattern) or fnmatch.fnmatch(
                f"{relative_str}/**", pattern
            ):
                return True

        return False

    def read_file(self, file_path: str) -> str:
        """
        Read file content.

        Args:
            file_path: Path to file (relative to repo or absolute)

        Returns:
            File content

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = self._resolve_path(file_path)

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, file_path: str, content: str, force: bool = False) -> None:
        """
        Write content to file.

        Args:
            file_path: Path to file (relative to repo or absolute)
            content: Content to write
            force: Override protection check

        Raises:
            PermissionError: If file is protected and force is False
        """
        path = self._resolve_path(file_path)

        if not force and self.is_protected(str(path)):
            raise PermissionError(f"File is protected: {path}")

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def list_files(
        self,
        directory: str = ".",
        pattern: str = "*",
        recursive: bool = False,
        include_dirs: bool = False,
    ) -> List[str]:
        """
        List files in directory.

        Args:
            directory: Directory to list (relative to repo or absolute)
            pattern: Glob pattern to match
            recursive: Search recursively
            include_dirs: Include directories in results

        Returns:
            List of file paths relative to repo root
        """
        dir_path = self._resolve_path(directory)

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        results = []

        if recursive:
            for path in dir_path.rglob(pattern):
                if path.is_file() or (include_dirs and path.is_dir()):
                    try:
                        rel_path = path.relative_to(self.repo_path)
                        results.append(str(rel_path))
                    except ValueError:
                        continue
        else:
            for path in dir_path.glob(pattern):
                if path.is_file() or (include_dirs and path.is_dir()):
                    try:
                        rel_path = path.relative_to(self.repo_path)
                        results.append(str(rel_path))
                    except ValueError:
                        continue

        return sorted(results)

    def find_files(self, pattern: str, directory: str = ".") -> List[str]:
        """
        Find files matching pattern recursively.

        Args:
            pattern: Glob pattern to match
            directory: Directory to search from

        Returns:
            List of matching file paths relative to repo root
        """
        return self.list_files(
            directory=directory, pattern=pattern, recursive=True, include_dirs=False
        )

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file info (size, modified time, etc.)
        """
        path = self._resolve_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stat = path.stat()

        return {
            "path": str(path.relative_to(self.repo_path)),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "protected": self.is_protected(str(path)),
        }

    def _resolve_path(self, file_path: str) -> Path:
        """
        Resolve file path to absolute path within repo.

        Args:
            file_path: Relative or absolute path

        Returns:
            Resolved absolute path
        """
        path = Path(file_path)

        if path.is_absolute():
            return path
        else:
            return (self.repo_path / path).resolve()
