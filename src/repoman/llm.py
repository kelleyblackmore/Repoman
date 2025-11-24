"""LLM integration for Repoman."""

import os
from typing import Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name
            **kwargs: Additional parameters for the model
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.kwargs = kwargs

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI.

        Args:
            prompt: Input prompt
            **kwargs: Override default parameters

        Returns:
            Generated text
        """
        params = {**self.kwargs, **kwargs}
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 2000)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        **kwargs,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name
            **kwargs: Additional parameters for the model
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.kwargs = kwargs

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Anthropic Claude.

        Args:
            prompt: Input prompt
            **kwargs: Override default parameters

        Returns:
            Generated text
        """
        params = {**self.kwargs, **kwargs}
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 2000)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text


class LLMClient:
    """Main LLM client that manages providers."""

    def __init__(self, provider: str = "openai", model: Optional[str] = None, **kwargs):
        """
        Initialize LLM client.

        Args:
            provider: Provider name ('openai' or 'anthropic')
            model: Model name (provider-specific default if not provided)
            **kwargs: Additional parameters for the provider
        """
        self.provider_name = provider.lower()

        if self.provider_name == "openai":
            model = model or "gpt-4"
            self.provider = OpenAIProvider(model=model, **kwargs)
        elif self.provider_name == "anthropic":
            model = model or "claude-3-sonnet-20240229"
            self.provider = AnthropicProvider(model=model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the configured provider.

        Args:
            prompt: Input prompt
            **kwargs: Override default parameters

        Returns:
            Generated text
        """
        return self.provider.generate(prompt, **kwargs)

    def generate_code_analysis(self, code: str, task: str) -> str:
        """
        Analyze code and generate suggestions.

        Args:
            code: Source code to analyze
            task: Task description

        Returns:
            Analysis and suggestions
        """
        prompt = f"""Analyze the following code and provide suggestions for: {task}

Code:
```
{code}
```

Provide a clear analysis and actionable suggestions."""

        return self.generate(prompt)

    def generate_code_refactor(self, code: str, instructions: str) -> str:
        """
        Generate refactored code.

        Args:
            code: Original source code
            instructions: Refactoring instructions

        Returns:
            Refactored code
        """
        prompt = f"""Refactor the following code according to these
instructions: {instructions}

Original code:
```
{code}
```

Provide ONLY the refactored code without explanations."""

        return self.generate(prompt)

    def generate_commit_message(self, diff: str) -> str:
        """
        Generate a commit message from git diff.

        Args:
            diff: Git diff output

        Returns:
            Commit message
        """
        prompt = f"""Generate a concise commit message for the following changes:

```
{diff}
```

Provide only the commit message in conventional commit format."""

        return self.generate(prompt, max_tokens=100)
