"""
Repoman - Autonomous Repository Agent

An autonomous agent that can read, write, refactor code, run tests,
and manage repository changes using LLM assistance.
"""

__version__ = "0.1.0"

from .agent import RepoAgent
from .config import Config

__all__ = ["RepoAgent", "Config"]
