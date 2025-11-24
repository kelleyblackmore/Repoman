"""Basic usage examples for Repoman."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from repoman import RepoAgent  # noqa: E402


def example_analyze_codebase():
    """Example: Analyze codebase structure."""
    print("=" * 60)
    print("Example 1: Analyze Codebase")
    print("=" * 60)

    agent = RepoAgent(repo_path=".")
    analysis = agent.analyze_codebase(patterns=["*.py", "*.yaml"])

    print(f"Total files: {analysis['total_files']}")
    print(f"Git branch: {analysis['git_status']['branch']}")
    print(f"Repository dirty: {analysis['git_status']['is_dirty']}")
    print()


def example_read_file():
    """Example: Read a file."""
    print("=" * 60)
    print("Example 2: Read File")
    print("=" * 60)

    agent = RepoAgent(repo_path=".")

    try:
        content = agent.read_file("README.md")
        lines = content.split("\n")
        print(f"README.md has {len(lines)} lines")
        print(f"First line: {lines[0]}")
    except Exception as e:
        print(f"Error reading file: {e}")
    print()


def example_analyze_file():
    """Example: Analyze a specific file."""
    print("=" * 60)
    print("Example 3: Analyze File (requires LLM API key)")
    print("=" * 60)

    # This requires API key to be set
    try:
        agent = RepoAgent(repo_path=".")
        analysis = agent.analyze_file(
            "src/repoman/config.py", "Identify areas for improvement"
        )
        print("Analysis:")
        print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
    except Exception as e:
        print(f"Note: LLM features require API key: {e}")
    print()


def example_git_operations():
    """Example: Git operations."""
    print("=" * 60)
    print("Example 4: Git Operations")
    print("=" * 60)

    agent = RepoAgent(repo_path=".")
    status = agent.git_ops.get_status()

    print(f"Current branch: {status['branch']}")
    print(f"Dirty: {status['is_dirty']}")
    print(f"Untracked files: {len(status['untracked'])}")
    print(f"Modified files: {len(status['modified'])}")

    # Get recent commits
    commits = agent.git_ops.get_recent_commits(count=3)
    print("\nRecent commits:")
    for commit in commits:
        print(f"  {commit['sha'][:8]}: {commit['message'][:50]}")
    print()


def example_dry_run():
    """Example: Using dry-run mode."""
    print("=" * 60)
    print("Example 5: Dry Run Mode")
    print("=" * 60)

    agent = RepoAgent(repo_path=".")
    agent.dry_run = True

    print("Dry run mode enabled - no actual changes will be made")
    print("Status:", agent.get_status()["dry_run"])
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 60)
    print(" REPOMAN - Autonomous Repository Agent Examples")
    print("*" * 60)
    print("\n")

    example_analyze_codebase()
    example_read_file()
    example_git_operations()
    example_dry_run()
    example_analyze_file()  # Last as it requires API key

    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
