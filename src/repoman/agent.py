"""Main autonomous agent for Repoman."""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .config import Config
from .llm import LLMClient
from .file_ops import FileOperations
from .git_ops import GitOperations
from .runner import Runner


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RepoAgent:
    """Autonomous repository agent that can read, write, and refactor code."""

    def __init__(
        self,
        repo_path: str = ".",
        config_path: Optional[str] = None,
    ):
        """
        Initialize the repository agent.

        Args:
            repo_path: Path to repository
            config_path: Path to configuration file
        """
        self.repo_path = Path(repo_path).resolve()
        self.config = Config(config_path)

        # Initialize components
        self._llm = None  # Lazy initialization
        self.file_ops = FileOperations(
            str(self.repo_path),
            protected_patterns=self.config.get("safety.protected_files"),
        )
        self.git_ops = GitOperations(
            str(self.repo_path),
            auto_commit=self.config.get("repository.auto_commit"),
        )
        self.runner = Runner(
            str(self.repo_path),
            timeout=self.config.get("tasks.timeout"),
        )

        self.dry_run = self.config.get("safety.dry_run", False)
        self.max_iterations = self.config.get("tasks.max_iterations", 5)

        logger.info(f"Initialized RepoAgent for repository: {self.repo_path}")

    @property
    def llm(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._llm is None:
            self._llm = self._init_llm()
        return self._llm

    def _init_llm(self) -> LLMClient:
        """Initialize LLM client from config."""
        provider = self.config.get("llm.provider", "openai")
        model = self.config.get("llm.model")
        temperature = self.config.get("llm.temperature", 0.7)
        max_tokens = self.config.get("llm.max_tokens", 2000)

        return LLMClient(
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def analyze_codebase(self, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the codebase structure.

        Args:
            patterns: File patterns to analyze (defaults to common code files)

        Returns:
            Analysis results
        """
        if patterns is None:
            patterns = ["*.py", "*.js", "*.go", "*.java", "*.ts"]

        files = []
        for pattern in patterns:
            files.extend(self.file_ops.find_files(pattern))

        analysis = {
            "total_files": len(files),
            "files": files[:100],  # Limit for display
            "git_status": self.git_ops.get_status(),
        }

        logger.info(f"Analyzed {len(files)} files matching patterns: {patterns}")
        return analysis

    def read_file(self, file_path: str) -> str:
        """
        Read a file from the repository.

        Args:
            file_path: Path to file

        Returns:
            File content
        """
        logger.info(f"Reading file: {file_path}")
        return self.file_ops.read_file(file_path)

    def write_file(self, file_path: str, content: str, commit: bool = True) -> None:
        """
        Write content to a file.

        Args:
            file_path: Path to file
            content: Content to write
            commit: Auto-commit the change

        Raises:
            PermissionError: If file is protected
        """
        logger.info(f"Writing to file: {file_path}")

        if self.dry_run:
            logger.info("[DRY RUN] Would write to file")
            return

        self.file_ops.write_file(file_path, content)

        if commit and self.config.get("repository.auto_commit"):
            self._auto_commit([file_path])

    def refactor_file(
        self, file_path: str, instructions: str, commit: bool = True
    ) -> str:
        """
        Refactor a file using LLM.

        Args:
            file_path: Path to file
            instructions: Refactoring instructions
            commit: Auto-commit the change

        Returns:
            Refactored content
        """
        logger.info(f"Refactoring file: {file_path}")

        original_content = self.read_file(file_path)
        refactored_content = self.llm.generate_code_refactor(
            original_content, instructions
        )

        # Clean up markdown code blocks if present
        refactored_content = self._clean_code_output(refactored_content)

        if self.dry_run:
            logger.info("[DRY RUN] Would refactor file")
            return refactored_content

        self.write_file(file_path, refactored_content, commit=commit)
        return refactored_content

    def analyze_file(self, file_path: str, task: str) -> str:
        """
        Analyze a file and get LLM suggestions.

        Args:
            file_path: Path to file
            task: Analysis task description

        Returns:
            Analysis and suggestions
        """
        logger.info(f"Analyzing file: {file_path}")

        content = self.read_file(file_path)
        analysis = self.llm.generate_code_analysis(content, task)

        return analysis

    def run_tests(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests.

        Args:
            test_path: Specific test file or directory

        Returns:
            Test results
        """
        logger.info("Running tests...")
        result = self.runner.run_tests(test_path=test_path)

        if result["success"]:
            logger.info("Tests passed!")
        else:
            logger.warning("Tests failed!")

        return result

    def run_command(self, command: str) -> Dict[str, Any]:
        """
        Run a shell command.

        Args:
            command: Command to run

        Returns:
            Command results
        """
        logger.info(f"Running command: {command}")
        return self.runner.run_command(command)

    def commit_changes(
        self,
        message: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Commit changes to git.

        Args:
            message: Commit message (auto-generated if None)
            files: Specific files to commit

        Returns:
            Commit SHA or None if dry run
        """
        if self.dry_run:
            logger.info("[DRY RUN] Would commit changes")
            return None

        # Generate message from diff if not provided
        if message is None:
            diff = self.git_ops.get_diff()
            if diff:
                message = self.llm.generate_commit_message(diff)
                # Clean up the message
                message = message.strip().strip("`").strip('"').strip("'")
            else:
                message = "[Repoman] Automated changes"

        # Add commit prefix from config
        prefix = self.config.get("repository.commit_message_prefix", "[Repoman]")
        if not message.startswith(prefix):
            message = f"{prefix} {message}"

        logger.info(f"Committing with message: {message}")
        commit_sha = self.git_ops.commit(message, files)
        logger.info(f"Created commit: {commit_sha[:8]}")

        return commit_sha

    def create_branch(self, branch_name: str, checkout: bool = True) -> None:
        """
        Create a new git branch.

        Args:
            branch_name: Branch name
            checkout: Checkout the new branch
        """
        prefix = self.config.get("repository.branch_prefix", "repoman/")
        if not branch_name.startswith(prefix):
            branch_name = f"{prefix}{branch_name}"

        logger.info(f"Creating branch: {branch_name}")

        if self.dry_run:
            logger.info("[DRY RUN] Would create branch")
            return

        self.git_ops.create_branch(branch_name, checkout)

    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a high-level task using LLM to plan and execute.

        Args:
            task_description: Description of the task to perform

        Returns:
            Task execution results
        """
        logger.info(f"Executing task: {task_description}")

        # Get current repo status
        analysis = self.analyze_codebase()

        # Generate task plan
        plan_prompt = f"""Given this repository structure and task,
create a step-by-step plan:

Repository info:
- Total files: {analysis['total_files']}
- Recent files: {', '.join(analysis['files'][:10])}
- Git status: {analysis['git_status']}

Task: {task_description}

Provide a numbered list of specific steps to accomplish this task."""

        plan = self.llm.generate(plan_prompt)
        logger.info(f"Generated plan:\n{plan}")

        return {
            "task": task_description,
            "plan": plan,
            "analysis": analysis,
            "status": "planned",
        }

    def _auto_commit(self, files: List[str]) -> None:
        """Auto-commit changes to specified files."""
        if not self.config.get("repository.auto_commit"):
            return

        try:
            diff = self.git_ops.get_diff()
            if diff:
                self.git_ops.add_files(files)
                self.commit_changes(files=files)
        except Exception as e:
            logger.warning(f"Auto-commit failed: {e}")

    def _clean_code_output(self, code: str) -> str:
        """
        Clean LLM code output by removing markdown formatting.

        Args:
            code: Code potentially wrapped in markdown

        Returns:
            Clean code
        """
        lines = code.strip().split("\n")

        # Remove markdown code fences
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.

        Returns:
            Status information
        """
        return {
            "repo_path": str(self.repo_path),
            "dry_run": self.dry_run,
            "git_status": self.git_ops.get_status(),
            "config": {
                "llm_provider": self.config.get("llm.provider"),
                "llm_model": self.config.get("llm.model"),
                "auto_commit": self.config.get("repository.auto_commit"),
            },
        }
