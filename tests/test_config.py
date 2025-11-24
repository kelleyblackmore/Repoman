"""Tests for configuration management."""

import tempfile
from pathlib import Path
from src.repoman.config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_default_config(self):
        """Test default configuration initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = Config(str(config_path))

            assert config.get("llm.provider") == "openai"
            assert config.get("llm.model") == "gpt-4"
            assert config.get("repository.auto_commit") is True

    def test_get_config_value(self):
        """Test getting configuration values."""
        config = Config()

        # Test existing value
        provider = config.get("llm.provider")
        assert provider in ["openai", "anthropic"]

        # Test default value
        assert config.get("nonexistent.key", "default") == "default"

    def test_set_config_value(self):
        """Test setting configuration values."""
        config = Config()

        config.set("llm.temperature", 0.5)
        assert config.get("llm.temperature") == 0.5

        config.set("new.nested.value", 123)
        assert config.get("new.nested.value") == 123

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"

            # Create and save config
            config1 = Config(str(config_path))
            config1.set("llm.model", "gpt-3.5-turbo")
            config1.set("custom.value", "test")
            config1.save()

            # Load config
            config2 = Config(str(config_path))
            assert config2.get("llm.model") == "gpt-3.5-turbo"
            assert config2.get("custom.value") == "test"
