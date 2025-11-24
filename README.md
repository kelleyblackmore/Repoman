# Repoman

**Autonomous Repository Agent** - A Python-based agent that runs on a schedule to read, write, refactor code, run tests, and manage repository changes using LLM assistance.

## Features

- 🤖 **LLM-Powered**: Uses OpenAI GPT-4 or Anthropic Claude for intelligent code analysis and refactoring
- 📝 **File Operations**: Read, write, and refactor code files safely
- 🔄 **Git Integration**: Automated commits, branch management, and PR creation
- 🧪 **Test Runner**: Execute tests and scripts automatically
- ⏰ **Scheduled Runs**: GitHub Actions workflow for automated scheduled execution
- 🛡️ **Safety Features**: Protected files, dry-run mode, and configurable safeguards
- 🔧 **Flexible Configuration**: YAML-based configuration for easy customization

## Installation

```bash
# Clone the repository
git clone https://github.com/kelleyblackmore/Repoman.git
cd Repoman

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```
OPENAI_API_KEY=your_key_here
# or
ANTHROPIC_API_KEY=your_key_here
```

3. Customize `config/repoman.yaml` to suit your needs.

## Usage

### Command Line Interface

```bash
# Show agent status
python -m src.repoman.cli status

# Analyze codebase
python -m src.repoman.cli analyze --patterns "*.py" "*.js"

# Read a file
python -m src.repoman.cli read path/to/file.py

# Refactor a file
python -m src.repoman.cli refactor path/to/file.py "Add type hints and docstrings"

# Analyze a specific file
python -m src.repoman.cli analyze-file path/to/file.py "Find potential bugs"

# Run tests
python -m src.repoman.cli test

# Execute a high-level task
python -m src.repoman.cli task "Improve error handling in all Python files"

# Create a branch
python -m src.repoman.cli branch feature/improvements

# Commit changes
python -m src.repoman.cli commit -m "Automated improvements"
```

### Python API

```python
from repoman import RepoAgent

# Initialize agent
agent = RepoAgent(repo_path=".", config_path="config/repoman.yaml")

# Analyze codebase
analysis = agent.analyze_codebase(patterns=["*.py"])

# Read a file
content = agent.read_file("src/example.py")

# Refactor a file
refactored = agent.refactor_file(
    "src/example.py",
    "Add type hints and improve documentation"
)

# Run tests
results = agent.run_tests()

# Execute a task
task_result = agent.execute_task("Refactor all Python files to follow PEP 8")

# Commit changes
commit_sha = agent.commit_changes(message="Automated refactoring")
```

## Scheduled Execution

The agent can run on a schedule using GitHub Actions:

1. **Set up secrets** in your GitHub repository:
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

2. **Configure the workflow** in `.github/workflows/scheduled-agent.yml`:
   - Edit the cron schedule (default: daily at 2 AM UTC)
   - Customize the tasks to execute
   - Enable/disable automatic PR creation

3. **Manual trigger**: You can also run the workflow manually from the Actions tab.

## Configuration Options

### LLM Configuration
- `provider`: Choose 'openai' or 'anthropic'
- `model`: Specific model to use (gpt-4, claude-3-sonnet-20240229, etc.)
- `temperature`: Creativity level (0.0-1.0)
- `max_tokens`: Maximum response length

### Repository Settings
- `auto_commit`: Automatically commit changes
- `commit_message_prefix`: Prefix for commit messages
- `branch_prefix`: Prefix for created branches
- `auto_pr`: Automatically create pull requests

### Safety Settings
- `dry_run`: Preview changes without making them
- `require_approval`: Require manual approval before changes
- `protected_files`: Patterns for files that cannot be modified

## Safety and Best Practices

1. **Start with dry-run mode**: Test the agent with `--dry-run` flag
2. **Protect critical files**: Configure `protected_files` in your config
3. **Review changes**: Always review commits before pushing
4. **Use branches**: Let the agent work on feature branches
5. **Monitor execution**: Check GitHub Actions logs regularly

## Example Workflows

### Daily Code Quality Improvements
```yaml
# .github/workflows/scheduled-agent.yml
- name: Improve code quality
  run: |
    python -m src.repoman.cli task "Add docstrings to functions without them"
    python -m src.repoman.cli test
```

### Automated Documentation Updates
```python
agent = RepoAgent()
agent.execute_task("Update README with any new features in the code")
agent.commit_changes()
```

### Refactoring Session
```python
agent = RepoAgent()
files = agent.file_ops.find_files("*.py")
for file in files:
    agent.refactor_file(file, "Improve error handling and add logging")
agent.run_tests()
agent.commit_changes()
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
```

### Linting
```bash
flake8 src/ tests/
```

## Architecture

```
Repoman/
├── src/repoman/
│   ├── __init__.py      # Package initialization
│   ├── agent.py         # Main RepoAgent class
│   ├── config.py        # Configuration management
│   ├── llm.py           # LLM provider integrations
│   ├── file_ops.py      # File system operations
│   ├── git_ops.py       # Git operations
│   ├── runner.py        # Test/script runner
│   └── cli.py           # Command-line interface
├── config/
│   └── repoman.yaml     # Configuration file
├── tests/               # Test suite
├── .github/workflows/   # GitHub Actions
└── requirements.txt     # Dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Review all automated changes before merging
- Configure protected files appropriately
- Use dry-run mode for testing

## Troubleshooting

**API Key Issues**: Ensure your API keys are set in `.env` or as environment variables

**Git Operations Fail**: Check that git is configured with user name and email

**Protected File Errors**: Adjust `protected_files` in config if needed

**Import Errors**: Run `pip install -e .` to install in development mode

## Support

For issues and questions, please open an issue on GitHub.