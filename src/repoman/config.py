"""Configuration management for Repoman."""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Manages configuration for the autonomous repo agent."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or "config/repoman.yaml"
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)

        if config_file.exists():
            with open(config_file, "r") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            "repository": {
                "auto_commit": True,
                "commit_message_prefix": "[Repoman]",
                "branch_prefix": "repoman/",
                "auto_pr": False,
            },
            "tasks": {
                "max_iterations": 5,
                "timeout": 300,
            },
            "safety": {
                "dry_run": False,
                "require_approval": False,
                "protected_files": [".git/**", ".github/**", "config/**"],
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation key.

        Args:
            key: Configuration key (e.g., 'llm.model')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot notation key.

        Args:
            key: Configuration key (e.g., 'llm.model')
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file.

        Args:
            path: Optional path to save to (defaults to self.config_path)
        """
        save_path = Path(path or self.config_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
