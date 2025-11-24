"""Tests for file operations."""

import pytest
import tempfile
from pathlib import Path
from src.repoman.file_ops import FileOperations


class TestFileOperations:
    """Test suite for FileOperations class."""

    def test_read_file(self):
        """Test reading a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_content = "Hello, World!"
            test_file.write_text(test_content)

            file_ops = FileOperations(tmpdir)
            content = file_ops.read_file("test.txt")

            assert content == test_content

    def test_write_file(self):
        """Test writing to a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_ops = FileOperations(tmpdir)
            file_ops.write_file("test.txt", "Test content")

            test_file = Path(tmpdir) / "test.txt"
            assert test_file.exists()
            assert test_file.read_text() == "Test content"

    def test_protected_files(self):
        """Test protected file patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_ops = FileOperations(
                tmpdir, protected_patterns=[".git/**", "config/**"]
            )

            assert file_ops.is_protected(".git/config")
            assert file_ops.is_protected("config/settings.yaml")
            assert not file_ops.is_protected("src/code.py")

    def test_write_protected_file(self):
        """Test that writing to protected files raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_ops = FileOperations(tmpdir, protected_patterns=["protected/**"])

            with pytest.raises(PermissionError):
                file_ops.write_file("protected/file.txt", "content")

    def test_list_files(self):
        """Test listing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "file1.py").write_text("print('1')")
            (Path(tmpdir) / "file2.py").write_text("print('2')")
            (Path(tmpdir) / "file3.txt").write_text("text")

            file_ops = FileOperations(tmpdir)

            # List all Python files
            py_files = file_ops.list_files(pattern="*.py")
            assert len(py_files) == 2
            assert "file1.py" in py_files
            assert "file2.py" in py_files

    def test_find_files_recursive(self):
        """Test finding files recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (Path(tmpdir) / "root.py").write_text("root")
            (subdir / "nested.py").write_text("nested")

            file_ops = FileOperations(tmpdir)
            py_files = file_ops.find_files("*.py")

            assert len(py_files) == 2

    def test_get_file_info(self):
        """Test getting file information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            file_ops = FileOperations(tmpdir)
            info = file_ops.get_file_info("test.txt")

            assert info["path"] == "test.txt"
            assert info["is_file"] is True
            assert info["size"] > 0
            assert "modified" in info
