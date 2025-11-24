# Repoman Quick Start Guide

## Installation

```bash
# Clone and install
git clone https://github.com/kelleyblackmore/Repoman.git
cd Repoman
pip install -e .

# Or just dependencies
pip install -r requirements.txt
```

## Configuration

1. Set your API key:
```bash
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"
```

2. (Optional) Customize config:
```bash
cp config/repoman.yaml config/my-config.yaml
# Edit config/my-config.yaml
```

## Basic Usage

### Command Line

```bash
# Check status
python -m src.repoman.cli status

# Analyze codebase
python -m src.repoman.cli analyze --patterns "*.py"

# Read a file
python -m src.repoman.cli read src/example.py

# Refactor a file
python -m src.repoman.cli refactor src/example.py "Add type hints"

# Run tests
python -m src.repoman.cli test

# Execute a task
python -m src.repoman.cli task "Improve error handling"

# Dry run mode
python -m src.repoman.cli --dry-run task "Add docstrings"
```

### Python API

```python
from repoman import RepoAgent

# Initialize
agent = RepoAgent(repo_path=".")

# Basic operations
analysis = agent.analyze_codebase()
content = agent.read_file("src/example.py")
agent.refactor_file("src/example.py", "Add type hints")

# Git operations
agent.commit_changes(message="Automated improvements")
agent.create_branch("feature/improvements")

# Run tests
results = agent.run_tests()
```

## Scheduled Automation

The agent can run on a schedule via GitHub Actions:

1. Add API key to repository secrets: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
2. Enable the workflow in `.github/workflows/scheduled-agent.yml`
3. Customize tasks in the workflow file

## Safety Features

- **Dry Run Mode**: Test without making changes
  ```bash
  python -m src.repoman.cli --dry-run task "refactor code"
  ```

- **Protected Files**: Configure in `config/repoman.yaml`:
  ```yaml
  safety:
    protected_files:
      - '.git/**'
      - '.github/**'
      - 'config/**'
  ```

- **Branch-based workflow**: Work on feature branches
  ```bash
  python -m src.repoman.cli branch feature/improvements
  ```

## Examples

Run the examples:
```bash
python examples/basic_usage.py
```

## Testing & Development

```bash
# Run tests
pytest tests/

# Format code
black src/ tests/ examples/

# Lint code
flake8 src/ tests/ examples/ --max-line-length=88
```

## Common Tasks

### 1. Code Quality Improvement
```bash
python -m src.repoman.cli task "Add docstrings to all functions"
```

### 2. Documentation Update
```bash
python -m src.repoman.cli task "Update README with new features"
```

### 3. Refactoring
```bash
python -m src.repoman.cli refactor src/module.py "Extract helper functions"
```

### 4. Analyze for Issues
```bash
python -m src.repoman.cli analyze-file src/module.py "Find potential bugs"
```

## Troubleshooting

**API Key Error**: Ensure environment variable is set
```bash
export OPENAI_API_KEY="your-key"
```

**Import Error**: Install in development mode
```bash
pip install -e .
```

**Git Error**: Configure git
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [config/repoman.yaml](config/repoman.yaml) for configuration options
3. Explore [examples/basic_usage.py](examples/basic_usage.py) for more examples
4. Set up scheduled runs with GitHub Actions
