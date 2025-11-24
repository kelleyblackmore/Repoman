"""Git operations for Repoman."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import git
from git import Repo, GitCommandError


class GitOperations:
    """Handles git operations for the autonomous agent."""

    def __init__(self, repo_path: str, auto_commit: bool = True):
        """
        Initialize git operations.

        Args:
            repo_path: Path to git repository
            auto_commit: Whether to auto-commit changes
        """
        self.repo_path = Path(repo_path).resolve()
        self.auto_commit = auto_commit

        try:
            self.repo = Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise ValueError(f"Not a git repository: {repo_path}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get repository status.

        Returns:
            Dictionary with status information
        """
        return {
            "branch": self.repo.active_branch.name,
            "is_dirty": self.repo.is_dirty(),
            "untracked": self.repo.untracked_files,
            "modified": [item.a_path for item in self.repo.index.diff(None)],
            "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
        }

    def get_diff(self, staged: bool = False) -> str:
        """
        Get git diff.

        Args:
            staged: Get diff of staged changes

        Returns:
            Diff output
        """
        if staged:
            return self.repo.git.diff("--cached")
        else:
            return self.repo.git.diff()

    def add_files(self, files: Optional[List[str]] = None) -> None:
        """
        Stage files for commit.

        Args:
            files: List of file paths (relative to repo). If None, adds all.
        """
        if files:
            self.repo.index.add(files)
        else:
            self.repo.git.add(A=True)

    def commit(self, message: str, files: Optional[List[str]] = None) -> str:
        """
        Commit changes.

        Args:
            message: Commit message
            files: Specific files to commit (None for all staged)

        Returns:
            Commit SHA

        Raises:
            ValueError: If nothing to commit
        """
        if files:
            self.add_files(files)

        if not self.repo.is_dirty() and not self.repo.untracked_files:
            raise ValueError("Nothing to commit")

        if files is None and not self.is_staged():
            # Stage all changes if nothing staged and no files specified
            self.add_files()

        commit = self.repo.index.commit(message)
        return commit.hexsha

    def is_staged(self) -> bool:
        """
        Check if there are staged changes.

        Returns:
            True if changes are staged
        """
        return len(list(self.repo.index.diff("HEAD"))) > 0

    def create_branch(self, branch_name: str, checkout: bool = True) -> None:
        """
        Create a new branch.

        Args:
            branch_name: Name of the branch
            checkout: Whether to checkout the new branch
        """
        new_branch = self.repo.create_head(branch_name)
        if checkout:
            new_branch.checkout()

    def checkout_branch(self, branch_name: str, create: bool = False) -> None:
        """
        Checkout a branch.

        Args:
            branch_name: Name of the branch
            create: Create branch if it doesn't exist
        """
        if create and branch_name not in self.repo.heads:
            self.create_branch(branch_name)
        else:
            self.repo.heads[branch_name].checkout()

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> None:
        """
        Push commits to remote.

        Args:
            remote: Remote name
            branch: Branch name (current branch if None)
        """
        if branch is None:
            branch = self.repo.active_branch.name

        origin = self.repo.remote(remote)
        origin.push(branch)

    def create_pull_request_info(self, title: str, body: str) -> Dict[str, str]:
        """
        Create pull request information.

        Note: This doesn't create a PR directly, but returns info needed
        for PR creation via GitHub CLI or API.

        Args:
            title: PR title
            body: PR description

        Returns:
            Dictionary with PR information
        """
        return {
            "title": title,
            "body": body,
            "head": self.repo.active_branch.name,
            "base": "main",
        }

    def apply_diff(self, diff_content: str) -> None:
        """
        Apply a git diff.

        Args:
            diff_content: Diff content to apply

        Raises:
            GitCommandError: If diff cannot be applied
        """
        try:
            self.repo.git.apply(["--3way"], input=diff_content.encode())
        except GitCommandError as e:
            raise GitCommandError(f"Failed to apply diff: {e}")

    def get_recent_commits(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commits.

        Args:
            count: Number of commits to retrieve

        Returns:
            List of commit information dictionaries
        """
        commits = []
        for commit in list(self.repo.iter_commits())[:count]:
            commits.append(
                {
                    "sha": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                }
            )
        return commits

    def reset_changes(self, hard: bool = False) -> None:
        """
        Reset uncommitted changes.

        Args:
            hard: Perform hard reset (discard all changes)
        """
        if hard:
            self.repo.git.reset("--hard")
        else:
            self.repo.git.reset()

    def get_file_history(self, file_path: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get commit history for a specific file.

        Args:
            file_path: Path to file (relative to repo)
            count: Number of commits to retrieve

        Returns:
            List of commit information for the file
        """
        commits = []
        for commit in list(self.repo.iter_commits(paths=file_path))[:count]:
            commits.append(
                {
                    "sha": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                }
            )
        return commits
