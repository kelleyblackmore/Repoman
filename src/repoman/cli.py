"""Command-line interface for Repoman."""

import argparse
import sys
import json

from .agent import RepoAgent
from .config import Config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Repoman - Autonomous Repository Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--repo",
        default=".",
        help="Path to repository (default: current directory)",
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status command
    subparsers.add_parser("status", help="Show agent status")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze codebase")
    analyze_parser.add_argument(
        "--patterns",
        nargs="+",
        help="File patterns to analyze (e.g., *.py *.js)",
    )

    # Read command
    read_parser = subparsers.add_parser("read", help="Read a file")
    read_parser.add_argument("file", help="File path")

    # Write command
    write_parser = subparsers.add_parser("write", help="Write to a file")
    write_parser.add_argument("file", help="File path")
    write_parser.add_argument("content", help="Content to write")
    write_parser.add_argument(
        "--no-commit", action="store_true", help="Don't auto-commit"
    )

    # Refactor command
    refactor_parser = subparsers.add_parser("refactor", help="Refactor a file")
    refactor_parser.add_argument("file", help="File path")
    refactor_parser.add_argument("instructions", help="Refactoring instructions")
    refactor_parser.add_argument(
        "--no-commit", action="store_true", help="Don't auto-commit"
    )

    # Analyze file command
    analyze_file_parser = subparsers.add_parser(
        "analyze-file", help="Analyze a specific file"
    )
    analyze_file_parser.add_argument("file", help="File path")
    analyze_file_parser.add_argument("task", help="Analysis task")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--path", help="Specific test file or directory")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a shell command")
    run_parser.add_argument("command", help="Command to execute")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("--message", "-m", help="Commit message")
    commit_parser.add_argument("--files", nargs="+", help="Specific files to commit")

    # Branch command
    branch_parser = subparsers.add_parser("branch", help="Create a branch")
    branch_parser.add_argument("name", help="Branch name")
    branch_parser.add_argument(
        "--no-checkout", action="store_true", help="Don't checkout the branch"
    )

    # Task command
    task_parser = subparsers.add_parser("task", help="Execute a high-level task")
    task_parser.add_argument("description", help="Task description")

    # Init config command
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument(
        "--output", default="config/repoman.yaml", help="Output path"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle init separately as it doesn't need agent
    if args.command == "init":
        config = Config()
        config.save(args.output)
        print(f"Configuration initialized at: {args.output}")
        return

    # Initialize agent
    try:
        agent = RepoAgent(repo_path=args.repo, config_path=args.config)
        if args.dry_run:
            agent.dry_run = True
    except Exception as e:
        print(f"Error initializing agent: {e}", file=sys.stderr)
        sys.exit(1)

    # Execute command
    try:
        if args.command == "status":
            status = agent.get_status()
            print(json.dumps(status, indent=2))

        elif args.command == "analyze":
            analysis = agent.analyze_codebase(patterns=args.patterns)
            print(json.dumps(analysis, indent=2))

        elif args.command == "read":
            content = agent.read_file(args.file)
            print(content)

        elif args.command == "write":
            agent.write_file(args.file, args.content, commit=not args.no_commit)
            print(f"Written to: {args.file}")

        elif args.command == "refactor":
            result = agent.refactor_file(
                args.file, args.instructions, commit=not args.no_commit
            )
            print(f"Refactored: {args.file}")
            print("\nRefactored content:")
            print(result)

        elif args.command == "analyze-file":
            analysis = agent.analyze_file(args.file, args.task)
            print(analysis)

        elif args.command == "test":
            result = agent.run_tests(test_path=args.path)
            print(f"Tests {'passed' if result['success'] else 'failed'}")
            if result["stdout"]:
                print("\nOutput:")
                print(result["stdout"])
            if result["stderr"]:
                print("\nErrors:")
                print(result["stderr"])
            sys.exit(0 if result["success"] else 1)

        elif args.command == "run":
            result = agent.run_command(args.command)
            print(f"Command {'succeeded' if result['success'] else 'failed'}")
            if result["stdout"]:
                print("\nOutput:")
                print(result["stdout"])
            if result["stderr"]:
                print("\nErrors:")
                print(result["stderr"])
            sys.exit(0 if result["success"] else 1)

        elif args.command == "commit":
            commit_sha = agent.commit_changes(message=args.message, files=args.files)
            if commit_sha:
                print(f"Created commit: {commit_sha[:8]}")
            else:
                print("No changes to commit (or dry run)")

        elif args.command == "branch":
            agent.create_branch(args.name, checkout=not args.no_checkout)
            print(f"Created branch: {args.name}")

        elif args.command == "task":
            result = agent.execute_task(args.description)
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
